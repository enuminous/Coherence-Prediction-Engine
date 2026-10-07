"""Verification of causality, experimental integrity, edge cases and stated scope."""
import csv
import json
import math
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cpe.core import Tracker,coherence,initialize,calibration_radius
from cpe.io import ROOT,REGISTRY,load_data,read_json,write_json,validate_protocol,verify_journal
from cpe.engine import freeze,run,verify_run,check_freeze,make_ticket,resolve_ticket
from cpe.atlas import atlas,coverage,verify_atlas

class NumericalContracts(unittest.TestCase):
    def test_coherence_bounds_extremes_and_scale(self):
        for x,m,e in [(0,0,1),(-3,7,.01),(1e308,-1e308,1e306),(4,4,.1)]:
            self.assertTrue(0<=coherence(x,m,e)<=1)
        self.assertEqual(coherence(4,4,.1),1)
        self.assertAlmostEqual(coherence(-3,7,.1),coherence(-30,70,1))

    def test_invalid_decay_and_nonfinite_rejected(self):
        for decay in (-.1,1,2,float('nan')):
            with self.assertRaises(ValueError): Tracker(0,0,0,1,decay=decay)
        for value in (float('nan'),float('inf')):
            with self.assertRaises(ValueError): coherence(value,0,1)

    def test_memory_forgets_initial_state_at_stated_rate(self):
        a=Tracker(.8,0,0,1,memory=5)
        b=Tracker(.8,0,0,1,memory=-2)
        rng=random.Random(7)
        for i in range(1,70):
            y=rng.uniform(-2,2)
            a.observe(y);b.observe(y)
            self.assertAlmostEqual(a.memory-b.memory,7*(.97**i),places=12)

    def test_bound_on_memory_for_bounded_innovations(self):
        tracker=Tracker(0,0,0,1,memory=.5)
        for i in range(500):
            tracker.observe(2 if i%3 else -2)
            self.assertLessEqual(abs(tracker.memory),2)

    def test_constant_signal_has_exact_forecasts(self):
        tracker=initialize([7]*40,.97,.01)
        self.assertEqual(set(tracker.predict().values()),{7})
        self.assertEqual(calibration_radius([0]*30,.1),0)

    def test_future_observation_cannot_change_current_forecast(self):
        a=Tracker(.8,.1,0,1,previous=1,memory=.4,last_coherence=.8)
        b=Tracker(**a.to_dict())
        forecast_a=a.predict();forecast_b=b.predict()
        a.observe(-100);b.observe(100)
        self.assertEqual(forecast_a,forecast_b)
        self.assertNotEqual(a.predict(),b.predict())

    def test_coherence_mapping_is_not_translation_invariant(self):
        # A documented limitation, not a suppressed negative result.
        self.assertNotEqual(coherence(0,1,.01),coherence(100,101,.01))

class ExperimentContracts(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.data=self.root/'data.csv'
        self.protocol_path=self.root/'protocol.json'
        protocol=read_json(ROOT/'protocols/control_null.json')
        protocol['bootstrap_samples']=200
        write_json(self.protocol_path,protocol)
        self.rows=[]
        rng=random.Random(31)
        y=0.
        for i in range(120):
            y=.8*y+rng.gauss(0,.2)
            self.rows.append(['s',i,y,'train' if i<40 else 'calibration' if i<80 else 'test',''])
        self.save_rows()

    def tearDown(self): self.temp.cleanup()

    def save_rows(self):
        with self.data.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['series','time','y','split','event']);w.writerows(self.rows)

    def frozen(self):
        path=self.root/'freeze.json'
        return path,freeze(self.data,self.protocol_path,path)

    def test_unsorted_duplicate_irregular_times_rejected(self):
        for bad in (self.rows[4][1],self.rows[4][1]-.5,self.rows[4][1]+.3):
            original=self.rows[5][1];self.rows[5][1]=bad;self.save_rows()
            with self.assertRaises(ValueError): load_data(self.data)
            self.rows[5][1]=original

    def test_training_after_test_is_rejected(self):
        self.rows[-1][3]='train';self.save_rows()
        with self.assertRaises(ValueError): load_data(self.data)

    def test_unknown_and_non_executable_equations_rejected(self):
        p=read_json(self.protocol_path)
        for eid in ('ME-001','ME-102','ME-999'):
            p['equation_ids']=[eid]
            with self.assertRaises(ValueError): validate_protocol(p)

    def test_file_or_source_change_invalidates_freeze(self):
        _,receipt=self.frozen()
        with patch('cpe.engine.source_manifest',return_value={}):
            with self.assertRaises(ValueError): check_freeze(self.data,receipt)
        self.rows[-1][2]+=1;self.save_rows()
        with self.assertRaises(ValueError): check_freeze(self.data,receipt)

    def test_run_integrity_missing_labels_and_no_overwrite(self):
        path,_=self.frozen();out=self.root/'run'
        summary=run(self.data,path,out)
        self.assertTrue(verify_run(out)['verified'])
        self.assertIsNone(summary['diagnostics']['normal_alert_rate'])
        self.assertEqual(summary['diagnostics']['label_coverage'],0)
        with self.assertRaises(FileExistsError): run(self.data,path,out)
        with (out/'predictions.csv').open('a') as f: f.write('tamper\n')
        with self.assertRaises(ValueError): verify_run(out)

    def test_reproduction_is_numerically_identical(self):
        path,_=self.frozen()
        a=run(self.data,path,self.root/'a');b=run(self.data,path,self.root/'b')
        self.assertEqual(a,b)

    def test_test_values_do_not_change_fit_or_calibration(self):
        from cpe.engine import calibrate
        p=read_json(self.protocol_path)
        rows=load_data(self.data)['s']
        a,radii_a,threshold_a=calibrate(rows,p)
        for row in rows:
            if row['split']=='test': row['y']+=1000
        b,radii_b,threshold_b=calibrate(rows,p)
        self.assertEqual(a.to_dict(),b.to_dict())
        self.assertEqual(radii_a,radii_b)
        self.assertEqual(threshold_a,threshold_b)

    def test_complete_ticket_resolution_cycle(self):
        path,_=self.frozen();run(self.data,path,self.root/'run')
        checkpoint=read_json(self.root/'run/checkpoints.json')['s']
        ticket=make_ticket(checkpoint,self.root/'ticket.json')
        self.assertEqual(ticket['time'],120)
        write_json(self.root/'observation.json',dict(series='s',time=120,y=.7,source='unit-test observation'))
        result=resolve_ticket(self.root/'ticket.json',self.root/'observation.json',self.root/'resolution.json')
        next_ticket=make_ticket(result['checkpoint'],self.root/'ticket2.json')
        self.assertEqual(next_ticket['time'],121)
        self.assertIn('absolute_errors',result)

    def test_mismatched_ticket_outcome_is_rejected(self):
        path,_=self.frozen();run(self.data,path,self.root/'run')
        checkpoint=read_json(self.root/'run/checkpoints.json')['s']
        make_ticket(checkpoint,self.root/'ticket.json')
        write_json(self.root/'wrong.json',dict(series='wrong',time=120,y=.7,source='test'))
        with self.assertRaises(ValueError): resolve_ticket(self.root/'ticket.json',self.root/'wrong.json',self.root/'resolution.json')

    def test_journal_reordering_is_detected(self):
        path,_=self.frozen();run(self.data,path,self.root/'run')
        p=self.root/'run/events.jsonl';lines=p.read_text().splitlines()
        lines[1],lines[2]=lines[2],lines[1];p.write_text('\n'.join(lines)+'\n')
        with self.assertRaises(ValueError): verify_journal(p)

class ScopeContracts(unittest.TestCase):
    def test_all_165_structural_counts(self):
        self.assertTrue(verify_atlas()['passed'])
        self.assertEqual(len(atlas()),165)

    def test_four_body_gap_reported(self):
        result=coverage(['E','M','S','F'],4)
        self.assertEqual(result['covered'],0)
        self.assertEqual(result['missing'],[['E','M','S','F']])

    def test_unknown_sector_rejected(self):
        with self.assertRaises(ValueError): coverage(['E','M','invented'],3)

    def test_registry_does_not_promote_unimplemented_equations(self):
        rows=read_json(REGISTRY/'equations.json')
        self.assertEqual(len(rows),102)
        executable=[r for r in rows if r['engine_binding']=='scalar_coherence_metric']
        self.assertEqual([r['id'] for r in executable],['ME-047'])
        self.assertEqual(next(r for r in rows if r['id']=='ME-102')['disposition'],'NOT_SATISFIED_BY_THIS_RELEASE')

if __name__=='__main__': unittest.main()

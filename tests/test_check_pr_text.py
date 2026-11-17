import importlib.util, re, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_pr_text', ROOT / 'scripts/check_pr_text.py')
pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr)
# Detector literals are assembled from fragments so this file stays clean.
A, B = 'pa' + 'x', 'mi' + 'mas'
WORKFLOW = ROOT / '.github/workflows/pr-text-privacy.yml'


class PullRequestTextTest(unittest.TestCase):
    def run_check(self, title, body):
        return pr.main({'PR_TITLE': title, 'PR_BODY': body})

    def test_clean_title_and_body_pass(self):
        self.assertEqual(self.run_check('Use role names for compute hosts',
                                        'Runs on the HPC host; preview on the workstation.'), 0)
        self.assertEqual(self.run_check('Empty description', ''), 0)

    def test_dirty_body_fails(self):
        for word in (A, B, B.title(), A.upper()):
            self.assertEqual(self.run_check('Clean title', 'Results\n\n- ' + word + ' accepted all jobs'), 1, word)

    def test_dirty_title_fails(self):
        self.assertEqual(self.run_check('Prepare full clustering on ' + B.title(), 'clean body'), 1)

    def test_missing_variables_fail_closed(self):
        self.assertEqual(pr.main({'PR_TITLE': 'x'}), 2)
        self.assertEqual(pr.main({}), 2)

    def test_matched_text_is_not_echoed(self):
        import contextlib, io
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.run_check('t', 'unique-marker-' + B + '-node')
        self.assertNotIn('unique-marker', err.getvalue())

    def test_workflow_passes_text_only_through_env(self):
        text = WORKFLOW.read_text()
        self.assertRegex(text, r'types:\s*\[opened, edited, synchronize, reopened\]')
        self.assertIn('PR_TITLE: ${{ github.event.pull_request.title }}', text)
        self.assertIn('PR_BODY: ${{ github.event.pull_request.body }}', text)
        self.assertFalse([l for l in text.splitlines() if 'run:' in l and '${{' in l])


if __name__ == '__main__':
    unittest.main()

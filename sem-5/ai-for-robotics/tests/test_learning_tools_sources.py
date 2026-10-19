"""Source-linked learning records and independently implemented grid arithmetic.

These checks do not certify independent author/reviewer separation or source
coverage. The observation records describe actual visual inspection separately.
"""
from __future__ import annotations

import heapq
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate  # noqa: E402


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SourceLinkedLearningChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = read("data/question-batches/search-foundations.json")
        cls.observations = {
            row["physicalPage"]: row
            for row in map(json.loads, (ROOT / "audits/learning-tools-page-observations.jsonl").read_text().splitlines())
        }

    def test_question_and_concept_schemas(self):
        question_schema = read("data/schema.question.json")
        concept_schema = read("data/schema.concept.json")
        for question in self.batch["questions"]:
            self.assertEqual(validate.schema_errors(question, question_schema), [], question["id"])
            self.assertEqual(len({o["id"] for o in question["options"]}), len(question["options"]))
            self.assertEqual(len({o["text"] for o in question["options"]}), len(question["options"]))
            self.assertEqual(set(question["solution"]["optionExplanations"]), {o["id"] for o in question["options"]})
        for concept in self.batch["concepts"]:
            self.assertEqual(validate.schema_errors(concept, concept_schema), [], concept["id"])

    def test_blind_packet_has_no_author_answer_fields(self):
        blind = read("audits/blind-search-foundations.json")
        questions = {q["id"]: q for q in self.batch["questions"]}
        self.assertEqual({q["id"] for q in blind}, set(questions))
        for question in blind:
            self.assertNotIn("solution", question)
            self.assertNotIn("correctOptionIds", question)
            self.assertEqual(question["options"], questions[question["id"]]["options"])
            self.assertEqual(question["stem"], questions[question["id"]]["stem"])

    def test_frozen_question_hashes_are_current(self):
        hashes = read("audits/search-foundations-validation.json")["questionHashes"]
        for question in self.batch["questions"]:
            self.assertEqual(validate.question_hash(question), hashes[question["id"]])

    def test_every_search_page_has_accountable_observation(self):
        for page in range(1105, 1138):
            row = self.observations[page]
            self.assertEqual(row["method"], "rendered_page")
            self.assertTrue(row["observedConcepts"])
            self.assertTrue((ROOT / row["evidenceArtifact"]).is_file())
            self.assertEqual(row["printedSlideNumberStatus"], "present")
            self.assertTrue(row["inspectorId"])
            if row["disposition"] == "excluded":
                self.assertTrue(row["exclusionReason"])
        self.assertEqual(self.observations[1135]["disposition"], "unresolved")

    def test_all_19_grid_cost_and_heuristic_entries(self):
        """Use independent Python, not the JavaScript search implementation."""
        walls = {(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (3, 2)}
        nodes = {(row, col) for row in range(5) for col in range(5)} - walls
        costs = {(4, 4): 0.0}
        frontier = [(0.0, (4, 4))]
        while frontier:
            cost, current = heapq.heappop(frontier)
            if cost > costs[current] + 1e-10:
                continue
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if not (dr or dc):
                        continue
                    successor = current[0] + dr, current[1] + dc
                    if successor not in nodes:
                        continue
                    if dr and dc and (
                        (current[0] + dr, current[1]) not in nodes
                        or (current[0], current[1] + dc) not in nodes
                    ):
                        continue
                    candidate = cost + (1.4 if dr and dc else 1.0)
                    if candidate + 1e-10 < costs.get(successor, float("inf")):
                        costs[successor] = candidate
                        heapq.heappush(frontier, (candidate, successor))
        g_table = self.observations[1133]["observedTables"]["gByRow"]
        h_table = self.observations[1134]["observedTables"]["hByRow"]
        self.assertEqual(len(nodes), 19)
        for row, col in nodes:
            dr, dc = abs(row - 2), col
            heuristic = 1.4 * min(dr, dc) + abs(dr - dc)
            self.assertAlmostEqual(costs[row, col], g_table[row][col], places=10)
            self.assertAlmostEqual(heuristic, h_table[row][col], places=10)
        for row, col in walls:
            self.assertIsNone(g_table[row][col])
            self.assertIsNone(h_table[row][col])

    def test_learning_records_have_real_source_references_not_synthetic_fill(self):
        bundle = read("data/learning-tools-draft.json")
        for records in bundle["learningTools"].values():
            for record in records:
                self.assertFalse(record.get("synthetic", False))
                self.assertTrue(record["sourceRefs"])
                for reference in record["sourceRefs"]:
                    self.assertEqual(reference["sourceId"], "lectures")
                    self.assertEqual(reference["slideId"], f"lectures-p{reference['physicalPage']:04d}")
                    self.assertTrue(reference["locator"])
                    self.assertTrue(reference["evidenceText"])
                    self.assertEqual(len(reference["sourceSha256"]), 64)


if __name__ == "__main__":
    unittest.main()

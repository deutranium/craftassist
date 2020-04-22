"""
Copyright (c) Facebook, Inc. and its affiliates.
"""

import unittest

import shapes
from mc_memory import MCAgentMemory
from .utils import Mob, Pos
from entities import MOBS_BY_ID
from base_craftassist_test_case import BaseCraftassistTestCase


class ObjectsTest(BaseCraftassistTestCase):
    def setUp(self):
        super().setUp()

        # add two objects
        self.obj_a = self.add_object([((0, 0, z), (41, 0)) for z in [0, -1, -2]])
        self.obj_b = self.add_object([((0, 0, z), (41, 0)) for z in [-4, -5]])

        # give them unique tags
        self.agent.memory.tag(self.obj_a.memid, "tag_A")
        self.agent.memory.tag(self.obj_b.memid, "tag_B")

    def test_merge_tags(self):
        obj = self.add_object([((0, 0, -3), (41, 0))])
        self.assertIn("tag_A", obj.get_tags())
        self.assertIn("tag_B", obj.get_tags())


class TriggersTests(BaseCraftassistTestCase):
    def setUp(self):
        super().setUp()
        self.cube_right = self.add_object(shapes.cube(bid=(42, 0)), (9, 63, 4))
        self.cube_left = self.add_object(shapes.cube(), (9, 63, 10))
        self.set_looking_at(list(self.cube_right.blocks.keys())[0])

    def test_workspace_cleared_on_object_delete(self):
        # Tag object
        tag = "fluff"
        self.handle_logical_form(
            {
                "dialogue_type": "PUT_MEMORY",
                "filters": {"reference_object": {"location": {"location_type": "SPEAKER_LOOK"}}},
                "upsert": {"memory_data": {"memory_type": "TRIPLE", "has_tag": tag}},
            }
        )
        self.assertIn(tag, self.cube_right.get_tags())

        # Destroy it
        changes = self.handle_logical_form(
            {
                "dialogue_type": "HUMAN_GIVE_COMMAND",
                "action": {"action_type": "DESTROY", "reference_object": {"has_tag": tag}},
            }
        )
        self.assertEqual(set(changes.keys()), set(self.cube_right.blocks.keys()))

        # Ensure it is not in recent entities
        recent_memids = [m.memid for m in self.agent.memory.get_recent_entities("BlockObjects")]
        self.assertNotIn(self.cube_right.memid, recent_memids)


class MethodsTests(unittest.TestCase):
    def setUp(self):
        self.memory = MCAgentMemory()

    def test_peek_empty(self):
        self.assertEqual(self.memory.task_stack_peek(), None)

    def test_add_mob(self):
        # add mob
        chicken = {v: k for k, v in MOBS_BY_ID.items()}["chicken"]
        mob_id, mob_type, pos = 42, chicken, Pos(3, 4, 5)
        self.memory.set_mob_position(Mob(mob_id, mob_type, pos))

        # get mob
        self.assertIsNotNone(self.memory.get_mob_by_eid(mob_id))

        # update mob
        pos = Pos(6, 7, 8)
        self.memory.set_mob_position(Mob(mob_id, mob_type, pos))

        # get mob
        mob_node = self.memory.get_mob_by_eid(mob_id)
        self.assertIsNotNone(mob_node)
        self.assertEqual(mob_node.pos, (6, 7, 8))

    def test_add_guardian_mob(self):
        guardian = {v: k for k, v in MOBS_BY_ID.items()}["guardian"]
        mob_id, mob_type, pos = 42, guardian, Pos(3, 4, 5)
        self.memory.set_mob_position(Mob(mob_id, mob_type, pos))


if __name__ == "__main__":
    unittest.main()

"""Advanced tests for task management features."""
import unittest
import os
import tempfile
from datetime import datetime
from database import init_db, get_db
from models import Task
from config import Config


class TestTaskPriority(unittest.TestCase):
    """Test task priority functionality."""

    def setUp(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        init_db()

    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_task_with_priority(self):
        """Test creating a task with priority."""
        task_id = Task.create(
            title="High priority task",
            owner="Ofek",
            priority="high"
        )
        self.assertIsNotNone(task_id)

        task = Task.get_by_id(task_id)
        self.assertEqual(task.priority, "high")

    def test_create_task_default_priority(self):
        """Test that default priority is medium."""
        task_id = Task.create(
            title="Normal task",
            owner="Shachar"
        )

        task = Task.get_by_id(task_id)
        self.assertEqual(task.priority, "medium")

    def test_update_task_priority(self):
        """Test updating task priority."""
        task_id = Task.create(
            title="Task to upgrade",
            owner="Ofek",
            priority="low"
        )

        success = Task.update_priority(task_id, "high")
        self.assertTrue(success)

        task = Task.get_by_id(task_id)
        self.assertEqual(task.priority, "high")

    def test_get_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        # Create tasks with different priorities
        Task.create(title="High 1", owner="Ofek", priority="high")
        Task.create(title="High 2", owner="Shachar", priority="high")
        Task.create(title="Low 1", owner="Ofek", priority="low")

        high_tasks = Task.get_by_priority("high")
        self.assertEqual(len(high_tasks), 2)
        self.assertTrue(all(t.priority == "high" for t in high_tasks))

    def test_invalid_priority_value(self):
        """Test that invalid priority values are rejected."""
        with self.assertRaises(ValueError):
            Task.create(
                title="Bad priority",
                owner="Ofek",
                priority="urgent"  # Not a valid priority
            )

    def test_priority_sorting(self):
        """Test that tasks are sorted by priority (high > medium > low)."""
        # Create tasks in random priority order
        Task.create(title="Low task", owner="Ofek", priority="low")
        Task.create(title="High task", owner="Ofek", priority="high")
        Task.create(title="Medium task", owner="Ofek", priority="medium")

        tasks = Task.get_all_open()
        # Should be sorted: high, medium, low
        self.assertEqual(tasks[0].priority, "high")
        self.assertEqual(tasks[1].priority, "medium")
        self.assertEqual(tasks[2].priority, "low")


class TestTaskCategories(unittest.TestCase):
    """Test task category/tag functionality."""

    def setUp(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        init_db()

    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_task_with_category(self):
        """Test creating a task with a category."""
        task_id = Task.create(
            title="Buy milk",
            owner="Ofek",
            category="shopping"
        )

        task = Task.get_by_id(task_id)
        self.assertEqual(task.category, "shopping")

    def test_create_task_without_category(self):
        """Test that category can be None."""
        task_id = Task.create(
            title="General task",
            owner="Shachar"
        )

        task = Task.get_by_id(task_id)
        self.assertIsNone(task.category)

    def test_get_tasks_by_category(self):
        """Test filtering tasks by category."""
        Task.create(title="Buy groceries", owner="Ofek", category="shopping")
        Task.create(title="Buy shoes", owner="Shachar", category="shopping")
        Task.create(title="Fix sink", owner="Ofek", category="home")

        shopping_tasks = Task.get_by_category("shopping")
        self.assertEqual(len(shopping_tasks), 2)
        self.assertTrue(all(t.category == "shopping" for t in shopping_tasks))

    def test_update_task_category(self):
        """Test updating task category."""
        task_id = Task.create(
            title="Task",
            owner="Ofek",
            category="work"
        )

        success = Task.update_category(task_id, "personal")
        self.assertTrue(success)

        task = Task.get_by_id(task_id)
        self.assertEqual(task.category, "personal")

    def test_get_all_categories(self):
        """Test getting list of all categories in use."""
        Task.create(title="Task 1", owner="Ofek", category="shopping")
        Task.create(title="Task 2", owner="Ofek", category="home")
        Task.create(title="Task 3", owner="Ofek", category="shopping")
        Task.create(title="Task 4", owner="Ofek", category="work")

        categories = Task.get_all_categories()
        self.assertEqual(set(categories), {"shopping", "home", "work"})


class TestCombinedFilters(unittest.TestCase):
    """Test combining priority and category filters."""

    def setUp(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        init_db()

    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_filter_by_priority_and_category(self):
        """Test filtering by both priority and category."""
        Task.create(title="High shopping", owner="Ofek", priority="high", category="shopping")
        Task.create(title="Low shopping", owner="Ofek", priority="low", category="shopping")
        Task.create(title="High home", owner="Ofek", priority="high", category="home")

        tasks = Task.get_by_filters(priority="high", category="shopping")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "High shopping")

    def test_filter_by_owner_priority_category(self):
        """Test filtering by owner, priority, and category."""
        Task.create(title="Ofek high shopping", owner="Ofek", priority="high", category="shopping")
        Task.create(title="Shachar high shopping", owner="Shachar", priority="high", category="shopping")
        Task.create(title="Ofek low shopping", owner="Ofek", priority="low", category="shopping")

        tasks = Task.get_by_filters(owner="Ofek", priority="high", category="shopping")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Ofek high shopping")


class TestTaskHistory(unittest.TestCase):
    """Test that priority and category changes are logged."""

    def setUp(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        init_db()

    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_priority_change_logged(self):
        """Test that priority changes are logged in history."""
        task_id = Task.create(title="Task", owner="Ofek", priority="low")
        Task.update_priority(task_id, "high")

        history = Task.get_history(task_id)
        # Should have: created, priority_changed
        self.assertGreaterEqual(len(history), 2)

        # Check that priority change was logged
        priority_changes = [h for h in history if h['action'] == 'priority_changed']
        self.assertEqual(len(priority_changes), 1)
        self.assertIn("high", priority_changes[0]['details'])

    def test_category_change_logged(self):
        """Test that category changes are logged in history."""
        task_id = Task.create(title="Task", owner="Ofek", category="work")
        Task.update_category(task_id, "personal")

        history = Task.get_history(task_id)

        # Check that category change was logged
        category_changes = [h for h in history if h['action'] == 'category_changed']
        self.assertEqual(len(category_changes), 1)
        self.assertIn("personal", category_changes[0]['details'])


class TestAPIIntegration(unittest.TestCase):
    """Test API endpoints with new features."""

    def setUp(self):
        """Set up test app and database."""
        from app import app
        self.db_fd, self.db_path = tempfile.mkstemp()
        Config.DATABASE_PATH = self.db_path
        init_db()

        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_create_task_with_priority_via_api(self):
        """Test creating task with priority via API."""
        response = self.client.post('/api/newTask', json={
            'title': 'API task',
            'owner': 'Ofek',
            'priority': 'high',
            'category': 'work'
        })

        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])

        task = Task.get_by_id(data['task_id'])
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.category, 'work')

    def test_filter_tasks_by_priority_via_api(self):
        """Test filtering tasks by priority via API."""
        Task.create(title="High 1", owner="Ofek", priority="high")
        Task.create(title="Low 1", owner="Ofek", priority="low")

        response = self.client.get('/api/tasks?priority=high')
        data = response.get_json()

        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['priority'], 'high')

    def test_filter_tasks_by_category_via_api(self):
        """Test filtering tasks by category via API."""
        Task.create(title="Shopping 1", owner="Ofek", category="shopping")
        Task.create(title="Home 1", owner="Ofek", category="home")

        response = self.client.get('/api/tasks?category=shopping')
        data = response.get_json()

        self.assertEqual(len(data['tasks']), 1)
        self.assertEqual(data['tasks'][0]['category'], 'shopping')


class TestWhatsAppParsing(unittest.TestCase):
    """Test WhatsApp message parsing with new fields."""

    def test_parse_priority_from_message(self):
        """Test parsing priority from WhatsApp message."""
        from app import parse_whatsapp_task

        message = """#task
Title: Important meeting
Owner: Ofek
Priority: high
Due: Tomorrow 5pm"""

        task_data = parse_whatsapp_task(message)
        self.assertEqual(task_data['priority'], 'high')

    def test_parse_category_from_message(self):
        """Test parsing category from WhatsApp message."""
        from app import parse_whatsapp_task

        message = """#task
Title: Buy groceries
Owner: Shachar
Category: shopping
Due: Today"""

        task_data = parse_whatsapp_task(message)
        self.assertEqual(task_data['category'], 'shopping')

    def test_parse_both_priority_and_category(self):
        """Test parsing both priority and category."""
        from app import parse_whatsapp_task

        message = """#task
Title: Fix broken door
Owner: Ofek
Priority: high
Category: home
Next: Call handyman"""

        task_data = parse_whatsapp_task(message)
        self.assertEqual(task_data['priority'], 'high')
        self.assertEqual(task_data['category'], 'home')


if __name__ == '__main__':
    unittest.main()

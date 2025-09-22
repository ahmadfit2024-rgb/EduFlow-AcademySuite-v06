# =================================================================
# apps/contracts/tests.py
# -----------------------------------------------------------------
# MIGRATION: Tests are updated to use standard ORM creation methods
# for the new relational models.
# =================================================================
from django.test import TestCase
from django.utils import timezone
from apps.users.models import CustomUser
from apps.contracts.models import Contract
from apps.learning.models import LearningPath

class ContractModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client_user = CustomUser.objects.create_user(
            username='clientcorp',
            role=CustomUser.Roles.THIRD_PARTY
        )
        cls.student_user = CustomUser.objects.create_user(
            username='studentundercontract',
            role=CustomUser.Roles.STUDENT
        )
        cls.learning_path = LearningPath.objects.create(
            title="Corporate Leadership Program"
        )

    def test_contract_creation(self):
        contract = Contract.objects.create(
            title="Q1 2025 Onboarding Contract",
            client=self.client_user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=90)
        )
        contract.enrolled_students.add(self.student_user)
        contract.learning_paths.add(self.learning_path)

        self.assertEqual(contract.title, "Q1 2025 Onboarding Contract")
        self.assertEqual(contract.client.username, 'clientcorp')
        self.assertEqual(contract.enrolled_students.count(), 1)
        self.assertEqual(contract.learning_paths.count(), 1)
        self.assertTrue(contract.is_active)
        self.assertIsNotNone(contract.created_at)

    def test_string_representation(self):
        contract = Contract.objects.create(
            title="Test String Representation",
            client=self.client_user,
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=30)
        )
        self.assertEqual(str(contract), "Test String Representation")
import sys
import unittest
from unittest.mock import MagicMock, patch

from qt_stylehelper.class_helpers import (
	RequireInitMeta, override, require_init, require_init_for_all_methods, require_qt, require_qt_for_all_methods,
)
from qt_stylehelper.errors import QtDependencyError


class TestRequireQtDecorator(unittest.TestCase):
	def setUp(self):
		"""Cleanup PySide6 from sys.modules before each test."""
		if "PySide6" in sys.modules:
			del sys.modules["PySide6"]

	def test_instance_method_with_qt_installed(self):
		"""Test instance method when PySide6 is installed."""
		with patch("sys.modules", {"PySide6": MagicMock()}):  # Mock PySide6 as installed
			class TestClass:
				@require_qt
				def instance_method(self):
					return "Instance method executed"

			obj = TestClass()
			self.assertEqual(obj.instance_method(), "Instance method executed")

	def test_instance_method_without_qt_installed(self):
		"""Test instance method when PySide6 is not installed."""

		class TestClass:
			@require_qt
			def instance_method(self):
				return "Instance method executed"

		obj = TestClass()
		with self.assertRaises(QtDependencyError) as context:
			obj.instance_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)

	def test_static_method_with_qt_installed(self):
		"""Test static method when PySide6 is installed."""
		with patch("sys.modules", {"PySide6": MagicMock()}):  # Mock PySide6 as installed
			class TestClass:
				@staticmethod
				@require_qt
				def static_method():
					return "Static method executed"

			self.assertEqual(TestClass.static_method(), "Static method executed")

	def test_static_method_without_qt_installed(self):
		"""Test static method when PySide6 is not installed."""

		class TestClass:
			@staticmethod
			@require_qt
			def static_method():
				return "Static method executed"

		with self.assertRaises(QtDependencyError) as context:
			TestClass.static_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)

	def test_class_method_with_qt_installed(self):
		"""Test class method when PySide6 is installed."""
		with patch("sys.modules", {"PySide6": MagicMock()}):  # Mock PySide6 as installed
			class TestClass:
				@classmethod
				@require_qt
				def class_method(cls):
					return "Class method executed"

			self.assertEqual(TestClass.class_method(), "Class method executed")

	def test_class_method_without_qt_installed(self):
		"""Test class method when PySide6 is not installed."""

		class TestClass:
			@classmethod
			@require_qt
			def class_method(cls):
				return "Class method executed"

		with self.assertRaises(QtDependencyError) as context:
			TestClass.class_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)


class RequireQtForAllMethodsTest(unittest.TestCase):
	@require_qt_for_all_methods
	class TestClass:
		def instance_method(self):
			return "Instance method called"

		@staticmethod
		def static_method():
			return "Static method called"

		@classmethod
		def class_method(cls):
			return "Class method called"

	def test_instance_method_with_qt_installed(self):
		"""Test instance method when PySide6 is installed"""
		with patch("sys.modules", {"PySide6": MagicMock()}):  # Mock PySide6 as installed
			obj = RequireQtForAllMethodsTest.TestClass()
			self.assertEqual(obj.instance_method(), "Instance method called")

	def test_instance_method_without_qt_installed(self):
		"""Test instance method when PySide6 is not installed"""
		obj = RequireQtForAllMethodsTest.TestClass()
		with self.assertRaises(QtDependencyError) as context:
			obj.instance_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)

	def test_static_method_with_qt_installed(self):
		"""Test static method when PySide6 is installed"""
		with patch("sys.modules", {"PySide6": MagicMock()}):
			self.assertEqual(RequireQtForAllMethodsTest.TestClass.static_method(), "Static method called")

	def test_static_method_without_qt_installed(self):
		"""Test static method when PySide6 is not installed"""
		with self.assertRaises(QtDependencyError) as context:
			RequireQtForAllMethodsTest.TestClass.static_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)

	def test_class_method_with_qt_installed(self):
		"""Test class method when PySide6 is installed"""
		with patch("sys.modules", {"PySide6": MagicMock()}):  # Mock PySide6 as installed
			self.assertEqual(RequireQtForAllMethodsTest.TestClass.class_method(), "Class method called")

	def test_class_method_without_qt_installed(self):
		"""Test class method when PySide6 is not installed"""
		with self.assertRaises(QtDependencyError) as context:
			RequireQtForAllMethodsTest.TestClass.class_method()
		self.assertEqual(
			str(context.exception), "A QT module is required. Please install PySide6."
		)


class RequireInitTest(unittest.TestCase):
	def test_require_init(self):
		class TestClass:
			def __init__(self):
				self._init = False

			@require_init
			def test_method(self):
				return "Initialized!"

		instance = TestClass()

		# Test: Calling method before initialization raises RuntimeError
		with self.assertRaises(RuntimeError) as context:
			instance.test_method()
		self.assertEqual(str(context.exception), "test_method cannot be called unless initialized.")

		# Test: Calling method after setting _init to True works
		instance._init = True
		result = instance.test_method()
		self.assertEqual(result, "Initialized!")


class RequireInitForAllMethodsTest(unittest.TestCase):
	def test_require_init_for_all_methods(self):
		@require_init_for_all_methods
		class TestClass:
			def __init__(self):
				self._init = False

			def method1(self):
				return "Method 1"

			def method2(self):
				return "Method 2"

		instance = TestClass()

		with self.assertRaises(RuntimeError) as context:
			instance.method1()
		self.assertEqual(str(context.exception), "method1 cannot be called unless initialized.")

		with self.assertRaises(RuntimeError) as context:
			instance.method2()
		self.assertEqual(str(context.exception), "method2 cannot be called unless initialized.")

		instance._init = True
		self.assertEqual(instance.method1(), "Method 1")
		self.assertEqual(instance.method2(), "Method 2")

	def test_require_init_for_all_methods_with_inheritance(self):
		class BaseClass:
			def base_method(self):
				return "Base Method"

		@require_init_for_all_methods
		class ChildClass(BaseClass):
			def __init__(self):
				self._init = False

			def child_method(self):
				return "Child Method"

		instance = ChildClass()

		with self.assertRaises(RuntimeError) as context:
			instance.base_method()
		self.assertEqual(str(context.exception), "base_method cannot be called unless initialized.")

		with self.assertRaises(RuntimeError) as context:
			instance.child_method()
		self.assertEqual(str(context.exception), "child_method cannot be called unless initialized.")

		instance._init = True
		self.assertEqual(instance.base_method(), "Base Method")
		self.assertEqual(instance.child_method(), "Child Method")


class RequireInitMetaTest(unittest.TestCase):
	def test_require_init_meta(self):
		# Define a test class with the RequireInitMeta metaclass
		class TestClass(metaclass=RequireInitMeta):
			def __init__(self):
				self._init = False

			def method1(self):
				return "Method 1"

			def method2(self):
				return "Method 2"

		instance = TestClass()

		# Test: All methods raise RuntimeError before initialization
		with self.assertRaises(RuntimeError) as context:
			instance.method1()
		self.assertEqual(str(context.exception), "method1 cannot be called unless initialized.")

		with self.assertRaises(RuntimeError) as context:
			instance.method2()
		self.assertEqual(str(context.exception), "method2 cannot be called unless initialized.")

		# Test: All methods work after setting _init to True
		instance._init = True
		self.assertEqual(instance.method1(), "Method 1")
		self.assertEqual(instance.method2(), "Method 2")

	def test_require_init_meta_with_base_class(self):
		# Define a base class with the RequireInitMeta metaclass
		class BaseClass(metaclass=RequireInitMeta):
			def __init__(self):
				self._init = False

			def base_method(self):
				return "Base Method"

		# Define a child class inheriting from the base class
		class ChildClass(BaseClass):
			def child_method(self):
				return "Child Method"

		# Create an instance of the child class
		instance = ChildClass()

		# Test: Base class method raises RuntimeError before initialization
		with self.assertRaises(RuntimeError) as context:
			instance.base_method()
		self.assertEqual(str(context.exception), "base_method cannot be called unless initialized.")

		# Test: Child class method raises RuntimeError before initialization
		with self.assertRaises(RuntimeError) as context:
			instance.child_method()
		self.assertEqual(str(context.exception), "child_method cannot be called unless initialized.")

		# Initialize the instance
		instance._init = True

		# Test: Base class method works after initialization
		self.assertEqual(instance.base_method(), "Base Method")

		# Test: Child class method works after initialization
		self.assertEqual(instance.child_method(), "Child Method")


class OverrideTest(unittest.TestCase):
	def test_valid_override(self):
		class Parent:
			def method_to_override(self):
				return "Parent method"

		class ValidChild(Parent):
			@override
			def method_to_override(self):
				return "Child method"

		# Test: ValidChild properly overrides the method
		instance = ValidChild()
		self.assertEqual(instance.method_to_override(), "Child method")

	def test_invalid_override(self):
		class Parent:
			def method_to_override(self):
				return "Parent method"

		class InvalidChild(Parent):
			@override
			def new_method(self):  # This does not override any method in Parent
				return "New method"

		# Test: InvalidChild raises an error when not overriding
		with self.assertRaises(AttributeError) as context:
			instance = InvalidChild()
			instance.new_method()
		self.assertIn("does not override any method in the base class", str(context.exception))

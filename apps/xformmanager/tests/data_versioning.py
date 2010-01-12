from xformmanager.tests.util import *
from xformmanager.xformdef import FormDef
from xformmanager.models import FormDataGroup
from decimal import Decimal
from datetime import *
import unittest

class DataVersioningTestCase(unittest.TestCase):
    """This class tests the creating of the form data management objects
       from different collections of forms."""

    def setUp(self):
        clear_data()
        self.original_formdef = create_xsd_and_populate("data/versioning/base.xsd")
        
    def tearDown(self):
        clear_data()
    
    def testFromSingle(self):
        """Tests the creation of a form group from a single form."""
        group = FormDataGroup.from_forms([self.original_formdef])
        self.assertEqual(1, len(group.forms.all()))
        self.assertEqual(self.original_formdef, group.forms.all()[0])
        columns = self.original_formdef.get_data_column_names()
        self.assertEqual(len(columns), len(group.columns.all()))
        for column in columns:
            # Make sure this returns exactly one.  By calling "get"
            # more or less than 1 will raise an exception
            column_def = group.columns.get(name=column)
            self.assertEqual(1, len(column_def.fields.all()))
            field = column_def.fields.all()[0]
            self.assertEqual(self.original_formdef, field.form)
            self.assertEqual(column, field.column_name)
    
    def testFromIdentical(self):
        """Tests the creation of a form group from two identical forms
           (with different version numbers)."""
        duplicate_formdef = create_xsd_and_populate("data/versioning/base.2.xsd")
        forms = [self.original_formdef, duplicate_formdef]
        group = FormDataGroup.from_forms(forms)
        self.assertEqual(2, len(group.forms.all()))
        for form in group.forms.all():
            self.assertTrue(form in forms)
        
        columns = self.original_formdef.get_data_column_names()
        self.assertEqual(len(columns), len(group.columns.all()))
        for column in columns:
            column_def = group.columns.get(name=column)
            self.assertEqual(2, len(column_def.fields.all()))
            for field in column_def.fields.all():
                self.assertTrue(field.form in forms)
                self.assertEqual(column, field.column_name)
    
    def testFull(self):
        """Tests the creation of a form group from several forms,
           including added, deleted, and changed fields."""
        fd2_dup = create_xsd_and_populate("data/versioning/base.2.xsd")
        fd3_add = create_xsd_and_populate("data/versioning/base.3.addition.xsd")
        fd4_del = create_xsd_and_populate("data/versioning/base.4.deletion.xsd")
        fd5_mod = create_xsd_and_populate("data/versioning/base.5.data_type_change.xsd")
        
        original_list = [self.original_formdef, fd2_dup, fd3_add, fd4_del, fd5_mod] 
                                          
        group = FormDataGroup.from_forms(original_list)
        self.assertEqual(5, len(group.forms.all()))
        for form in group.forms.all():
            self.assertTrue(form in original_list)
        
        columns = self.original_formdef.get_data_column_names()
        # this is added by form 3
        columns.append("meta_added_field")
        # a second one of these is added by form 5
        columns.append("meta_username")
        self.assertEqual(len(columns), len(group.columns.all()))
        
        for form in original_list:
            self._check_columns(form, group)
            
    def _check_columns(self, form, group):
        columns = form.get_data_column_names()
        column_types = form.get_data_column_types()
        column_map = dict(zip(columns, column_types))
        group_columns = group.columns.filter(fields__form=form)
        self.assertEqual(len(columns), len(group_columns))
        for column in group_columns:
            self.assertTrue(column.name in column_map)
            self.assertEqual(column.data_type, column_map[column.name])
            
            
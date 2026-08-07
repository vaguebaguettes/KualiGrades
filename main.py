# main.py
"""
PNG Simulator Calculator - Kivy Android App
UMPSA Bachelor of Electrical Engineering with Honours
"""

import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
import csv
import os
import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from functools import partial

# Window size for desktop testing
Window.size = (380, 700)

# ==================== DATA MODELS ====================

@dataclass
class Subject:
    code: str
    name: str
    credit: int
    is_placeholder: bool = False

@dataclass
class Grade:
    letter: str
    grade_point: float

@dataclass
class SubjectResult:
    subject: Subject
    grade: Grade
    semester: int = 0


# ==================== GRADE DATABASE ====================

class GradeDatabase:
    GRADES = {
        'A': 4.00, 'A-': 3.67, 'B+': 3.33, 'B': 3.00,
        'B-': 2.67, 'C+': 2.33, 'C': 2.00, 'C-': 1.67,
        'D+': 1.33, 'D': 1.00, 'E': 0.67, 'F': 0.00,
    }
    
    COMPULSORY_GRADES = {'HL': 0.00, 'HG': 0.00}
    
    @classmethod
    def get_all_grades(cls):
        return {**cls.GRADES, **cls.COMPULSORY_GRADES}
    
    @classmethod
    def is_valid_grade(cls, grade_letter: str) -> bool:
        return grade_letter in cls.get_all_grades()
    
    @classmethod
    def get_grade_point(cls, grade_letter: str) -> float:
        return cls.get_all_grades().get(grade_letter, 0.0)
    
    @classmethod
    def get_grade_options(cls) -> List[str]:
        return list(cls.get_all_grades().keys())


# ==================== SUBJECT DATABASE ====================

class SubjectDatabase:
    DEFAULT_SUBJECTS = {
        # First Year
        'BEL1113': ('Fundamental of Electrical Engineering', 3),
        'BC1103': ('Computer Programming', 3),
        'BEL1213': ('Digital Electronics', 3),
        'BEL1123': ('Circuit Analysis 1', 3),
        'BEL1233': ('Analog Electronics', 3),
        'BEL1133': ('Instrumentation & Measurements', 3),
        'BEL1113I': ('Instrumentation & Measurements Lab', 1),
        
        # Second Year
        'KUK2443': ('Numerical Methods & Optimization', 3),
        'BEL2123': ('Electromagnetic Fields Theory 1', 3),
        'BEL2113': ('Circuit Analysis 2', 3),
        'BEL2313': ('Principles of Communication Systems', 3),
        'BEL2612': ('Electrical Engineering Laboratory 1', 2),
        'KUK2142': ('Engineering Economics', 2),
        'BEL2323': ('Principles of Control Systems', 3),
        'BEL2133': ('Electromagnetic Fields Theory 2', 3),
        'BEL2413': ('Electrical Power System', 3),
        'BEL2622': ('Electrical Engineering Laboratory 2', 2),
        
        # Third Year
        'KUK3562': ('Occupational Safety & Health', 2),
        'BEL3213': ('Signal & Systems', 3),
        'BEL3111': ('Engineering Design Principle', 1),
        'BEL3513': ('Electrical Machines', 3),
        'BEL3612': ('Electrical Engineering Laboratory 3', 2),
        'KUK3022': ('Engineers in Society', 2),
        'BEL3423': ('Power System Analysis', 3),
        'BEL3523': ('Power Electronics', 3),
        'BEL3622': ('Electrical Engineering Laboratory 4', 2),
        'BEL3715': ('Integrated Design Project', 4),
        
        # Fourth Year
        'KUK4412': ('Project Management', 2),
        'BEL3413': ('Electrical Installation Design', 3),
        'BEL4413': ('Electrical Power Generation and High Voltage Engineering', 3),
        'BEL4423': ('Power System Operation & Control', 3),
        'BEL4513': ('Electronic Drives & Applications', 3),
        'BEL4113': ('Electrical Energy Utilisation', 3),
        'BEL4712': ('Undergraduate Research Project 1', 2),
        'BEL4724': ('Undergraduate Research Project 2', 4),
        
        # Electives
        'BEL4433': ('Power Quality', 3),
        'BEL4443': ('Renewable Energy System', 3),
        'BEL4523': ('Power System Protection', 3),
        'BEL4223': ('Embedded Controller Technology', 3),
        'BEL4213': ('Rapid Digital System Prototyping', 3),
        'BEL4313': ('Microwave Engineering', 3),
        'BEL4453': ('Forensic Engineering', 3),
        'BEL4333': ('Intelligent Control', 3),
        'BEL4373': ('Robotics', 3),
        'BEL3715T': ('Industrial Training', 5),
        
        # MPU Courses
        'MPU3422': ('MPU Course', 2),
        'MPU3412': ('MPU Course', 2),
        'MPU3113': ('MPU Course', 3),
        'MPU3123': ('MPU Course', 3),
        'ULE3722': ('Creative Writing', 2),
        'UHC1012': ('Falsafah Dan Isu Semasa', 2),
    }
    
    _subjects = None
    _store = None
    STORE_FILE = 'subjects_db.json'
    
    @classmethod
    def _initialize_store(cls):
        if cls._store is None:
            try:
                cls._store = JsonStore(cls.STORE_FILE)
            except:
                cls._store = JsonStore(cls.STORE_FILE)
        
        if not cls._store or not cls._store.keys():
            cls.reset_to_defaults()
    
    @classmethod
    def reset_to_defaults(cls):
        """Reset database to default subjects"""
        cls._subjects = dict(cls.DEFAULT_SUBJECTS)
        cls._save_to_store()
    
    @classmethod
    def _save_to_store(cls):
        """Save current subjects to JSON store"""
        try:
            if cls._store is None:
                cls._initialize_store()
            
            # Clear existing data
            for key in list(cls._store.keys()):
                cls._store.delete(key)
            
            # Save each subject
            for code, (name, credit) in cls._subjects.items():
                cls._store.put(code, name=name, credit=credit)
        except Exception as e:
            print(f"Error saving subjects: {e}")
    
    @classmethod
    def load_from_store(cls):
        """Load subjects from JSON store"""
        try:
            cls._initialize_store()
            
            if not cls._store or not cls._store.keys():
                cls.reset_to_defaults()
                return
            
            loaded = {}
            for code in cls._store.keys():
                try:
                    data = cls._store.get(code)
                    name = data.get('name', code)
                    credit = data.get('credit', cls.extract_credit_from_code(code))
                    loaded[code] = (name, credit)
                except:
                    continue
            
            if loaded:
                cls._subjects = loaded
            else:
                cls.reset_to_defaults()
        except Exception as e:
            print(f"Error loading subjects: {e}")
            cls.reset_to_defaults()
    
    @classmethod
    def get_all_subjects(cls) -> Dict:
        """Get all subjects as dict"""
        if cls._subjects is None:
            cls.load_from_store()
        return cls._subjects
    
    @classmethod
    def extract_credit_from_code(cls, code: str) -> int:
        digits = re.findall(r'\d', code)
        if digits:
            try:
                last_digit = int(digits[-1])
                if 1 <= last_digit <= 6:
                    return last_digit
            except ValueError:
                pass
        return 3
    
    @classmethod
    def get_subject(cls, code: str) -> Optional[Subject]:
        if cls._subjects is None:
            cls.load_from_store()
        
        code_upper = code.upper()
        if code_upper in cls._subjects:
            name, credit = cls._subjects[code_upper]
            return Subject(code_upper, name, credit, is_placeholder=False)
        
        # Create placeholder
        credit = cls.extract_credit_from_code(code)
        return Subject(code, f"{code} (Unknown)", credit, is_placeholder=True)
    
    @classmethod
    def search_subjects(cls, query: str) -> List[Subject]:
        if cls._subjects is None:
            cls.load_from_store()
        
        query_lower = query.lower()
        results = []
        for code, (name, credit) in cls._subjects.items():
            if query_lower in code.lower() or query_lower in name.lower():
                results.append(Subject(code, name, credit, is_placeholder=False))
        return results
    
    @classmethod
    def get_subject_names(cls) -> List[str]:
        if cls._subjects is None:
            cls.load_from_store()
        
        names = []
        for code, (name, credit) in cls._subjects.items():
            names.append(f"{code} - {name} ({credit} credits)")
        return sorted(names)
    
    @classmethod
    def add_subject(cls, code: str, name: str, credit: int) -> bool:
        """Add a new subject to database"""
        if cls._subjects is None:
            cls.load_from_store()
        
        code = code.upper()
        if code in cls._subjects:
            return False  # Subject already exists
        
        cls._subjects[code] = (name, credit)
        cls._save_to_store()
        return True
    
    @classmethod
    def update_subject(cls, code: str, name: str, credit: int) -> bool:
        """Update an existing subject"""
        if cls._subjects is None:
            cls.load_from_store()
        
        code = code.upper()
        if code not in cls._subjects:
            return False
        
        cls._subjects[code] = (name, credit)
        cls._save_to_store()
        return True
    
    @classmethod
    def delete_subject(cls, code: str) -> bool:
        """Delete a subject from database"""
        if cls._subjects is None:
            cls.load_from_store()
        
        code = code.upper()
        if code not in cls._subjects:
            return False
        
        del cls._subjects[code]
        try:
            if cls._store and code in cls._store.keys():
                cls._store.delete(code)
        except:
            pass
        cls._save_to_store()
        return True
    
    @classmethod
    def get_subject_count(cls) -> int:
        if cls._subjects is None:
            cls.load_from_store()
        return len(cls._subjects)


# ==================== PNG CALCULATOR ====================

class PNGCalculator:
    @staticmethod
    def calculate_png(results: List[SubjectResult]) -> Tuple[float, float, float]:
        total_grade_points = 0.0
        total_credits = 0
        
        for result in results:
            grade_points = result.grade.grade_point * result.subject.credit
            total_grade_points += grade_points
            total_credits += result.subject.credit
        
        if total_credits == 0:
            return 0.0, 0.0, 0.0
        
        png = total_grade_points / total_credits
        return total_grade_points, total_credits, png
    
    @staticmethod
    def calculate_pngk(all_results: List[SubjectResult]) -> Tuple[float, float, float, Dict[int, float]]:
        total_grade_points = 0.0
        total_credits = 0
        semester_data = {}
        
        for result in all_results:
            sem = result.semester
            if sem not in semester_data:
                semester_data[sem] = []
            semester_data[sem].append(result)
        
        semester_pngs = {}
        for sem, results in semester_data.items():
            points, credits, png = PNGCalculator.calculate_png(results)
            total_grade_points += points
            total_credits += credits
            semester_pngs[sem] = png
        
        if total_credits == 0:
            return 0.0, 0.0, 0.0, semester_pngs
        
        pngk = total_grade_points / total_credits
        return total_grade_points, total_credits, pngk, semester_pngs
    
    @staticmethod
    def get_classification(png: float) -> Tuple[str, str]:
        if png >= 3.67:
            return "First Class Honours", "🏆"
        elif png >= 3.33:
            return "Upper Second Class Honours", "🥈"
        elif png >= 2.67:
            return "Lower Second Class Honours", "🥉"
        elif png >= 2.00:
            return "Third Class Honours", "📗"
        else:
            return "Pass", "📕"


# ==================== CUSTOM WIDGETS ====================

class ModernButton(Button):
    def __init__(self, color=(0.2, 0.6, 0.9, 1), **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        self.size_hint_y = None
        self.height = 48
        self.font_size = 15
        self.bold = True
        self.button_color = color
        self.rect = None
        
        # Draw initial background
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.button_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

class SubjectEntry(BoxLayout):
    def __init__(self, grade_options, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 8
        self.size_hint_y = None
        self.height = 44
        self.padding = [5, 2]
        self.rect = None
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        
        self.subject_input = TextInput(
            hint_text='Subject Code',
            size_hint_x=0.42,
            multiline=False,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=14,
            padding=[10, 8]
        )
        self.add_widget(self.subject_input)
        
        self.grade_spinner = Spinner(
            text='Grade',
            values=grade_options,
            size_hint_x=0.28,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            font_size=14
        )
        self.add_widget(self.grade_spinner)
        
        self.remove_btn = Button(
            text='X',
            size_hint_x=0.15,
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=16,
            bold=True
        )
        self.add_widget(self.remove_btn)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])


class SemesterEntry(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = 6
        self.size_hint_y = None
        self.height = 44
        self.padding = [5, 2]
        self.rect = None
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.update_canvas()
        
        self.sem_input = TextInput(
            hint_text='Sem',
            size_hint_x=0.2,
            multiline=False,
            input_filter='int',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=14,
            padding=[8, 8]
        )
        self.add_widget(self.sem_input)
        
        self.subject_input = TextInput(
            hint_text='Subject Code',
            size_hint_x=0.38,
            multiline=False,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=14,
            padding=[10, 8]
        )
        self.add_widget(self.subject_input)
        
        self.grade_spinner = Spinner(
            text='Grade',
            values=GradeDatabase.get_grade_options(),
            size_hint_x=0.25,
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.1, 0.1, 0.1, 1),
            font_size=14
        )
        self.add_widget(self.grade_spinner)
        
        self.remove_btn = Button(
            text='X',
            size_hint_x=0.12,
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=16,
            bold=True
        )
        self.add_widget(self.remove_btn)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])


# ==================== SCREENS ====================

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=[15, 10, 15, 10], spacing=10)
        
        # Header
        header = BoxLayout(orientation='vertical', size_hint_y=0.15, padding=[20, 20])
        header.bind(pos=self._update_header_rect, size=self._update_header_rect)
        
        with header.canvas.before:
            Color(0.05, 0.25, 0.6, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[20, 20, 20, 20])
        
        title = Label(
            text='PNG Simulator\nUMPSA',
            color=(1, 1, 1, 1),
            font_size=28,
            bold=True,
            halign='center'
        )
        header.add_widget(title)
        layout.add_widget(header)
        
        # Menu buttons
        menu_layout = GridLayout(cols=2, spacing=12, size_hint_y=0.7, padding=[5, 5])
        
        buttons = [
            ('Semester PNG', (0.2, 0.6, 0.9, 1), self.go_to_png),
            ('PNGK Calculator', (0.3, 0.7, 0.4, 1), self.go_to_pngk),
            ('Target PNGK', (0.9, 0.6, 0.2, 1), self.go_to_target),
            ('Subject DB', (0.6, 0.3, 0.8, 1), self.go_to_subjects),
            ('Saved Data', (0.8, 0.4, 0.2, 1), self.go_to_saved),
            ('Import CSV', (0.2, 0.7, 0.7, 1), self.go_to_import),
            ('Manage DB', (0.5, 0.2, 0.6, 1), self.go_to_manage_db),
            ('Reset DB', (0.8, 0.2, 0.2, 1), self.reset_database),
        ]
        
        for text, color, callback in buttons:
            btn = ModernButton(text=text, color=color)
            btn.bind(on_press=callback)
            menu_layout.add_widget(btn)
        
        layout.add_widget(menu_layout)
        
        # Footer with subject count
        self.footer = Label(
            text=f'Subjects: {SubjectDatabase.get_subject_count()} | UMPSA Electrical Engineering',
            color=(0.5, 0.5, 0.5, 1),
            font_size=11,
            size_hint_y=0.05
        )
        layout.add_widget(self.footer)
        
        self.add_widget(layout)
    
    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def go_to_png(self, instance):
        self.manager.current = 'png_calculator'
    
    def go_to_pngk(self, instance):
        self.manager.current = 'pngk_calculator'
    
    def go_to_target(self, instance):
        self.manager.current = 'target_calculator'
    
    def go_to_subjects(self, instance):
        self.manager.current = 'subject_database'
    
    def go_to_saved(self, instance):
        self.manager.current = 'saved_data'
    
    def go_to_import(self, instance):
        self.manager.current = 'import_csv'
    
    def go_to_manage_db(self, instance):
        self.manager.current = 'manage_database'
    
    def reset_database(self, instance):
        """Reset database to default with confirmation"""
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text="⚠️ This will reset the database to default subjects.\n\nAny custom subjects will be lost.\n\nAre you sure?",
            halign='center',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14
        )
        popup_layout.add_widget(content_label)
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        confirm_btn = ModernButton(
            text='Yes, Reset',
            color=(0.9, 0.3, 0.3, 1),
            height=45
        )
        
        cancel_btn = ModernButton(
            text='Cancel',
            color=(0.5, 0.5, 0.5, 1),
            height=45
        )
        
        popup = Popup(
            title='Reset Database?',
            content=popup_layout,
            size_hint=(0.85, 0.4),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        
        def do_reset(btn):
            SubjectDatabase.reset_to_defaults()
            self.footer.text = f'Subjects: {SubjectDatabase.get_subject_count()} | UMPSA Electrical Engineering'
            popup.dismiss()
            self.show_toast('✅ Database reset to defaults')
        
        confirm_btn.bind(on_press=do_reset)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        popup_layout.add_widget(btn_layout)
        popup.open()
    
    def show_toast(self, message):
        """Simple toast notification"""
        popup = Popup(
            title='',
            content=Label(text=message, color=(0.1, 0.1, 0.1, 1)),
            size_hint=(0.8, 0.2),
            background_color=(0.9, 0.9, 0.9, 1)
        )
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        popup.open()


class PNGCalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_entries = []
        self.grade_options = GradeDatabase.get_grade_options()
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Semester PNG', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Semester input
        sem_layout = BoxLayout(size_hint_y=0.07, spacing=10, padding=[5, 0])
        sem_label = Label(text='Semester:', size_hint_x=0.25, bold=True, color=(0.2, 0.2, 0.2, 1))
        sem_layout.add_widget(sem_label)
        self.semester_input = TextInput(
            hint_text='1-8',
            multiline=False,
            input_filter='int',
            size_hint_x=0.75,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=15,
            padding=[12, 10]
        )
        sem_layout.add_widget(self.semester_input)
        main_layout.add_widget(sem_layout)
        
        # Subject entries area
        scroll = ScrollView(do_scroll_x=False, bar_width=3)
        self.entries_grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0, 5])
        self.entries_grid.bind(minimum_height=self.entries_grid.setter('height'))
        scroll.add_widget(self.entries_grid)
        main_layout.add_widget(scroll)
        
        # Buttons row
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        add_btn = ModernButton(
            text='Add Subject', 
            color=(0.2, 0.7, 0.3, 1),
            height=45
        )
        add_btn.bind(on_press=self.add_subject_entry)
        btn_layout.add_widget(add_btn)
        
        calc_btn = ModernButton(
            text='Calculate', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        calc_btn.bind(on_press=self.calculate)
        btn_layout.add_widget(calc_btn)
        
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)
        self.add_subject_entry(None)
    
    def add_subject_entry(self, instance):
        entry = SubjectEntry(self.grade_options)
        entry.remove_btn.bind(on_press=partial(self.remove_subject_entry, entry))
        self.entries_grid.add_widget(entry)
        self.subject_entries.append(entry)
    
    def remove_subject_entry(self, entry, instance):
        if len(self.subject_entries) > 1:
            self.entries_grid.remove_widget(entry)
            self.subject_entries.remove(entry)
    
    def calculate(self, instance):
        semester = self.semester_input.text.strip()
        if not semester:
            self.show_popup('Error', 'Please enter semester number', '❌')
            return
        
        try:
            sem = int(semester)
            if sem < 1 or sem > 8:
                self.show_popup('Error', 'Semester must be between 1 and 8', '❌')
                return
        except ValueError:
            self.show_popup('Error', 'Invalid semester number', '❌')
            return
        
        results = []
        for entry in self.subject_entries:
            code = entry.subject_input.text.strip()
            grade_letter = entry.grade_spinner.text
            
            if not code:
                continue
            
            if grade_letter == 'Grade' or not GradeDatabase.is_valid_grade(grade_letter):
                continue
            
            subject = SubjectDatabase.get_subject(code)
            grade = Grade(grade_letter, GradeDatabase.get_grade_point(grade_letter))
            results.append(SubjectResult(subject, grade, sem))
        
        if not results:
            self.show_popup('Error', 'No valid subjects entered', '❌')
            return
        
        # Calculate
        total_points, total_credits, png = PNGCalculator.calculate_png(results)
        classification, icon = PNGCalculator.get_classification(png)
        
        # Show results
        result_text = f"{icon} PNG: {png:.3f}\n"
        result_text += f"Classification: {classification}\n"
        result_text += f"Total Credits: {total_credits}\n"
        result_text += f"Total Points: {total_points:.2f}\n\n"
        result_text += "Subjects:\n"
        
        for r in results:
            result_text += f"  - {r.subject.code} - {r.grade.letter}\n"
        
        self.show_popup('Results', result_text, icon)
    
    def show_popup(self, title, content, icon="📊"):
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=content, 
            halign='left',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            text_size=(300, None)
        )
        popup_layout.add_widget(content_label)
        
        btn = ModernButton(
            text='Close', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.85, 0.65),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn)
        popup.open()


class PNGKCalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_entries = []
        self.grade_options = GradeDatabase.get_grade_options()
        self.store = JsonStore('pngk_data.json') if os.path.exists('pngk_data.json') else None
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='PNGK Calculator', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Info label
        info = Label(
            text='Enter all subjects from all semesters',
            size_hint_y=0.04,
            color=(0.5, 0.5, 0.5, 1),
            font_size=13,
            italic=True
        )
        main_layout.add_widget(info)
        
        # Subject entries area
        scroll = ScrollView(do_scroll_x=False, bar_width=3)
        self.entries_grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0, 5])
        self.entries_grid.bind(minimum_height=self.entries_grid.setter('height'))
        scroll.add_widget(self.entries_grid)
        main_layout.add_widget(scroll)
        
        # Buttons row
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        
        add_btn = ModernButton(
            text='Add Subject', 
            color=(0.2, 0.7, 0.3, 1),
            height=45
        )
        add_btn.bind(on_press=self.add_subject_entry)
        btn_layout.add_widget(add_btn)
        
        calc_btn = ModernButton(
            text='Calculate', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        calc_btn.bind(on_press=self.calculate)
        btn_layout.add_widget(calc_btn)
        
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)
        self.add_subject_entry(None)
    
    def add_subject_entry(self, instance):
        entry = SemesterEntry()
        entry.remove_btn.bind(on_press=partial(self.remove_subject_entry, entry))
        self.entries_grid.add_widget(entry)
        self.subject_entries.append(entry)
    
    def remove_subject_entry(self, entry, instance):
        if len(self.subject_entries) > 1:
            self.entries_grid.remove_widget(entry)
            self.subject_entries.remove(entry)
    
    def calculate(self, instance):
        results = []
        for entry in self.subject_entries:
            sem_text = entry.sem_input.text.strip()
            code = entry.subject_input.text.strip()
            grade_letter = entry.grade_spinner.text
            
            if not sem_text or not code:
                continue
            
            if grade_letter == 'Grade' or not GradeDatabase.is_valid_grade(grade_letter):
                continue
            
            try:
                sem = int(sem_text)
                if sem < 1 or sem > 8:
                    continue
            except ValueError:
                continue
            
            subject = SubjectDatabase.get_subject(code)
            grade = Grade(grade_letter, GradeDatabase.get_grade_point(grade_letter))
            results.append(SubjectResult(subject, grade, sem))
        
        if not results:
            self.show_popup('Error', 'No valid subjects entered', '❌')
            return
        
        # Calculate PNGK
        total_points, total_credits, pngk, semester_pngs = PNGCalculator.calculate_pngk(results)
        classification, icon = PNGCalculator.get_classification(pngk)
        
        # Build result text
        result_text = f"{icon} PNGK: {pngk:.3f}\n"
        result_text += f"Classification: {classification}\n"
        result_text += f"Total Credits: {total_credits}\n"
        result_text += f"Total Points: {total_points:.2f}\n\n"
        result_text += "Semester PNGs:\n"
        
        for sem, png in sorted(semester_pngs.items()):
            result_text += f"  - Semester {sem}: {png:.3f}\n"
        
        self.show_popup('PNGK Results', result_text, icon)
    
    def show_popup(self, title, content, icon="📈"):
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=content, 
            halign='left',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            text_size=(300, None)
        )
        popup_layout.add_widget(content_label)
        
        btn = ModernButton(
            text='Close', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.85, 0.65),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn)
        popup.open()


class TargetCalculatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.subject_entries = []
        self.grade_options = GradeDatabase.get_grade_options()
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Target PNGK', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Target input
        target_layout = BoxLayout(size_hint_y=0.07, spacing=10, padding=[5, 0])
        target_label = Label(
            text='Target PNGK:', 
            size_hint_x=0.35, 
            bold=True, 
            color=(0.2, 0.2, 0.2, 1)
        )
        target_layout.add_widget(target_label)
        self.target_input = TextInput(
            hint_text='3.00',
            multiline=False,
            input_filter='float',
            size_hint_x=0.65,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=15,
            padding=[12, 10]
        )
        target_layout.add_widget(self.target_input)
        main_layout.add_widget(target_layout)
        
        # Current known subjects area
        info = Label(
            text='Known Subjects (Previous Semesters)',
            size_hint_y=0.04,
            color=(0.2, 0.4, 0.7, 1),
            font_size=13,
            bold=True
        )
        main_layout.add_widget(info)
        
        scroll = ScrollView(do_scroll_x=False, size_hint_y=0.25, bar_width=3)
        self.entries_grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0, 5])
        self.entries_grid.bind(minimum_height=self.entries_grid.setter('height'))
        scroll.add_widget(self.entries_grid)
        main_layout.add_widget(scroll)
        
        add_btn = ModernButton(
            text='Add Known Subject', 
            color=(0.2, 0.7, 0.3, 1),
            height=40
        )
        add_btn.bind(on_press=self.add_subject_entry)
        main_layout.add_widget(add_btn)
        
        # Unknown subjects area
        info2 = Label(
            text='Unknown Subjects (Current Semester)',
            size_hint_y=0.04,
            color=(0.8, 0.4, 0.1, 1),
            font_size=13,
            bold=True
        )
        main_layout.add_widget(info2)
        
        scroll2 = ScrollView(do_scroll_x=False, size_hint_y=0.2, bar_width=3)
        self.unknown_grid = GridLayout(cols=1, spacing=8, size_hint_y=None, padding=[0, 5])
        self.unknown_grid.bind(minimum_height=self.unknown_grid.setter('height'))
        scroll2.add_widget(self.unknown_grid)
        main_layout.add_widget(scroll2)
        
        add_unknown_btn = ModernButton(
            text='Add Unknown Subject', 
            color=(0.9, 0.6, 0.2, 1),
            height=40
        )
        add_unknown_btn.bind(on_press=self.add_unknown_entry)
        main_layout.add_widget(add_unknown_btn)
        
        calc_btn = ModernButton(
            text='Calculate Target', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        calc_btn.bind(on_press=self.calculate)
        main_layout.add_widget(calc_btn)
        
        self.add_widget(main_layout)
        self.add_subject_entry(None)
    
    def add_subject_entry(self, instance):
        entry = SubjectEntry(self.grade_options)
        entry.remove_btn.bind(on_press=partial(self.remove_subject_entry, entry))
        self.entries_grid.add_widget(entry)
        self.subject_entries.append(entry)
    
    def remove_subject_entry(self, entry, instance):
        if len(self.subject_entries) > 1:
            self.entries_grid.remove_widget(entry)
            self.subject_entries.remove(entry)
    
    def add_unknown_entry(self, instance):
        entry = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=44, padding=[5, 2])
        
        # Add white background
        entry.bind(pos=self._update_unknown_rect, size=self._update_unknown_rect)
        with entry.canvas.before:
            Color(1, 1, 1, 1)
            entry.rect = RoundedRectangle(pos=entry.pos, size=entry.size, radius=[8])
        
        code_input = TextInput(
            hint_text='Subject Code', 
            size_hint_x=0.55, 
            multiline=False,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=14,
            padding=[10, 8]
        )
        entry.add_widget(code_input)
        
        credit_input = TextInput(
            hint_text='Credits', 
            size_hint_x=0.28, 
            multiline=False, 
            input_filter='int',
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=14,
            padding=[10, 8]
        )
        entry.add_widget(credit_input)
        
        remove_btn = Button(
            text='X', 
            size_hint_x=0.12, 
            background_color=(0.9, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            font_size=16,
            bold=True
        )
        remove_btn.bind(on_press=partial(self.remove_unknown_entry, entry))
        entry.add_widget(remove_btn)
        
        self.unknown_grid.add_widget(entry)
        
        # Store references to inputs
        entry.code_input = code_input
        entry.credit_input = credit_input
    
    def _update_unknown_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def remove_unknown_entry(self, entry, instance):
        self.unknown_grid.remove_widget(entry)
    
    def calculate(self, instance):
        target_text = self.target_input.text.strip()
        if not target_text:
            self.show_popup('Error', 'Please enter target PNGK', '❌')
            return
        
        try:
            target = float(target_text)
            if target < 0 or target > 4.0:
                self.show_popup('Error', 'Target must be between 0.00 and 4.00', '❌')
                return
        except ValueError:
            self.show_popup('Error', 'Invalid target PNGK', '❌')
            return
        
        # Process known subjects
        known_results = []
        total_points = 0.0
        total_credits = 0
        
        for entry in self.subject_entries:
            code = entry.subject_input.text.strip()
            grade_letter = entry.grade_spinner.text
            
            if not code or grade_letter == 'Grade' or not GradeDatabase.is_valid_grade(grade_letter):
                continue
            
            subject = SubjectDatabase.get_subject(code)
            grade = Grade(grade_letter, GradeDatabase.get_grade_point(grade_letter))
            known_results.append(SubjectResult(subject, grade, 0))
            total_points += grade.grade_point * subject.credit
            total_credits += subject.credit
        
        # Process unknown subjects
        unknown_subjects = []
        unknown_credits = 0
        
        for child in self.unknown_grid.children:
            if hasattr(child, 'code_input') and hasattr(child, 'credit_input'):
                code = child.code_input.text.strip()
                credit_text = child.credit_input.text.strip()
                
                if code and credit_text:
                    try:
                        credit = int(credit_text)
                        if credit > 0:
                            subject = Subject(code, f"{code} (Unknown)", credit, True)
                            unknown_subjects.append(subject)
                            unknown_credits += credit
                    except ValueError:
                        pass
        
        if not known_results and not unknown_subjects:
            self.show_popup('Error', 'No subjects entered', '❌')
            return
        
        # Calculate
        total_credits_all = total_credits + unknown_credits
        total_needed = target * total_credits_all
        needed_points = total_needed - total_points
        
        # Build result
        result_text = f"Target: {target:.3f}\n"
        result_text += f"Known: {total_credits} credits\n"
        result_text += f"Unknown: {unknown_credits} credits\n"
        result_text += f"Current Points: {total_points:.2f}\n"
        result_text += f"Points Needed: {needed_points:.2f}\n\n"
        
        if unknown_subjects and needed_points > 0:
            avg_needed = needed_points / unknown_credits if unknown_credits > 0 else 0
            
            result_text += "Average needed per credit:\n"
            result_text += f"  {avg_needed:.2f} points\n\n"
            result_text += "Recommended grades:\n"
            
            for subject in unknown_subjects:
                required_gp = needed_points / unknown_credits
                best_grade = 'D'
                best_diff = float('inf')
                for grade, gp in GradeDatabase.GRADES.items():
                    diff = abs(gp - required_gp)
                    if diff < best_diff:
                        best_diff = diff
                        best_grade = grade
                result_text += f"  - {subject.code}: {best_grade}\n"
        
        elif needed_points <= 0:
            result_text += "You've already achieved your target!\n"
        else:
            result_text += "Need higher grades to achieve target.\n"
        
        # Check if achievable
        best_possible = total_points + (4.0 * unknown_credits)
        best_pngk = best_possible / total_credits_all if total_credits_all > 0 else 0
        
        if best_pngk < target:
            result_text += f"\nTarget not achievable!\n"
            result_text += f"Best possible: {best_pngk:.3f} (all A's)"
        
        self.show_popup('Target Analysis', result_text)
    
    def show_popup(self, title, content, icon="🎯"):
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=content, 
            halign='left',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            text_size=(300, None)
        )
        popup_layout.add_widget(content_label)
        
        btn = ModernButton(
            text='Close', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.85, 0.7),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn)
        popup.open()


class SubjectDatabaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Subject Database', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Search
        search_layout = BoxLayout(size_hint_y=0.07, spacing=10)
        self.search_input = TextInput(
            hint_text='Search subjects...', 
            multiline=False, 
            size_hint_x=0.8,
            background_color=(0.95, 0.95, 0.95, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            hint_text_color=(0.5, 0.5, 0.5, 1),
            font_size=15,
            padding=[12, 10]
        )
        search_layout.add_widget(self.search_input)
        search_btn = ModernButton(
            text='Search', 
            size_hint_x=0.2,
            color=(0.2, 0.5, 0.9, 1),
            height=44
        )
        search_btn.bind(on_press=self.search)
        search_layout.add_widget(search_btn)
        main_layout.add_widget(search_layout)
        
        # Results
        scroll = ScrollView(do_scroll_x=False, bar_width=3)
        self.results_grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=[5, 5])
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))
        scroll.add_widget(self.results_grid)
        main_layout.add_widget(scroll)
        
        # Show all initially
        self.show_all()
        
        self.add_widget(main_layout)
    
    def show_all(self):
        self.results_grid.clear_widgets()
        subjects = SubjectDatabase.get_subject_names()
        for subject in subjects[:20]:
            label = Label(
                text=subject,
                size_hint_y=None,
                height=32,
                color=(0.2, 0.2, 0.2, 1),
                font_size=13,
                text_size=(350, None),
                halign='left'
            )
            self.results_grid.add_widget(label)
        if len(subjects) > 20:
            label = Label(
                text=f'... and {len(subjects) - 20} more subjects',
                size_hint_y=None,
                height=30,
                color=(0.5, 0.5, 0.5, 1),
                font_size=12,
                italic=True
            )
            self.results_grid.add_widget(label)
    
    def search(self, instance):
        query = self.search_input.text.strip()
        self.results_grid.clear_widgets()
        
        if not query:
            self.show_all()
            return
        
        results = SubjectDatabase.search_subjects(query)
        if not results:
            label = Label(
                text='No matching subjects found',
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1),
                font_size=14
            )
            self.results_grid.add_widget(label)
        else:
            for subject in results:
                text = f"{subject.code} - {subject.name} ({subject.credit} credits)"
                label = Label(
                    text=text,
                    size_hint_y=None,
                    height=32,
                    color=(0.2, 0.2, 0.2, 1),
                    font_size=13,
                    text_size=(350, None),
                    halign='left'
                )
                self.results_grid.add_widget(label)


class ManageDatabaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_edit_code = None
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Manage Database', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Add/Edit form
        form_box = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=5, padding=[5, 5])
        form_box.bind(pos=self._update_form_rect, size=self._update_form_rect)
        with form_box.canvas.before:
            Color(0.95, 0.95, 0.98, 1)
            self.form_rect = RoundedRectangle(pos=form_box.pos, size=form_box.size, radius=[10])
        
        form_title = Label(
            text='Add New Subject',
            size_hint_y=0.2,
            color=(0.1, 0.3, 0.6, 1),
            font_size=15,
            bold=True
        )
        self.form_title = form_title
        form_box.add_widget(form_title)
        
        # Code input
        code_layout = BoxLayout(size_hint_y=0.25, spacing=5)
        code_layout.add_widget(Label(text='Code:', size_hint_x=0.2, color=(0.2, 0.2, 0.2, 1), font_size=14))
        self.code_input = TextInput(
            multiline=False,
            size_hint_x=0.8,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            padding=[10, 8]
        )
        code_layout.add_widget(self.code_input)
        form_box.add_widget(code_layout)
        
        # Name input
        name_layout = BoxLayout(size_hint_y=0.25, spacing=5)
        name_layout.add_widget(Label(text='Name:', size_hint_x=0.2, color=(0.2, 0.2, 0.2, 1), font_size=14))
        self.name_input = TextInput(
            multiline=False,
            size_hint_x=0.8,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            padding=[10, 8]
        )
        name_layout.add_widget(self.name_input)
        form_box.add_widget(name_layout)
        
        # Credit input
        credit_layout = BoxLayout(size_hint_y=0.25, spacing=5)
        credit_layout.add_widget(Label(text='Credits:', size_hint_x=0.2, color=(0.2, 0.2, 0.2, 1), font_size=14))
        self.credit_input = TextInput(
            multiline=False,
            input_filter='int',
            size_hint_x=0.3,
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            padding=[10, 8]
        )
        credit_layout.add_widget(self.credit_input)
        
        self.save_btn = ModernButton(
            text='Add Subject',
            color=(0.2, 0.7, 0.3, 1),
            size_hint_x=0.5,
            height=40
        )
        self.save_btn.bind(on_press=self.save_subject)
        credit_layout.add_widget(self.save_btn)
        
        self.cancel_btn = ModernButton(
            text='Cancel',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_x=0.3,
            height=40
        )
        self.cancel_btn.bind(on_press=self.cancel_edit)
        credit_layout.add_widget(self.cancel_btn)
        self.cancel_btn.opacity = 0
        self.cancel_btn.disabled = True
        
        form_box.add_widget(credit_layout)
        main_layout.add_widget(form_box)
        
        # Subject list
        list_label = Label(
            text='Subject List',
            size_hint_y=0.04,
            color=(0.1, 0.3, 0.6, 1),
            font_size=14,
            bold=True
        )
        main_layout.add_widget(list_label)
        
        scroll = ScrollView(do_scroll_x=False, bar_width=3, size_hint_y=0.55)
        self.list_grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=[5, 5])
        self.list_grid.bind(minimum_height=self.list_grid.setter('height'))
        scroll.add_widget(self.list_grid)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.refresh_list()
    
    def _update_form_rect(self, instance, value):
        if hasattr(self, 'form_rect'):
            self.form_rect.pos = instance.pos
            self.form_rect.size = instance.size
    
    def refresh_list(self):
        self.list_grid.clear_widgets()
        subjects = SubjectDatabase.get_all_subjects()
        
        if not subjects:
            label = Label(
                text='No subjects in database',
                size_hint_y=None,
                height=40,
                color=(0.5, 0.5, 0.5, 1),
                font_size=14
            )
            self.list_grid.add_widget(label)
            return
        
        for code, (name, credit) in sorted(subjects.items()):
            # Create a row for each subject
            row = BoxLayout(size_hint_y=None, height=40, spacing=5, padding=[5, 2])
            
            # White background for row
            row.bind(pos=self._update_row_rect, size=self._update_row_rect)
            with row.canvas.before:
                Color(1, 1, 1, 1)
                row.rect = RoundedRectangle(pos=row.pos, size=row.size, radius=[6])
            
            # Subject info
            info = Label(
                text=f"{code}\n{name} ({credit}cr)",
                size_hint_x=0.6,
                color=(0.2, 0.2, 0.2, 1),
                font_size=12,
                halign='left',
                text_size=(200, None)
            )
            row.add_widget(info)
            
            # Edit button
            edit_btn = Button(
                text='Edit',
                size_hint_x=0.2,
                background_color=(0.2, 0.5, 0.9, 1),
                color=(1, 1, 1, 1),
                font_size=13,
                bold=True
            )
            edit_btn.bind(on_press=partial(self.edit_subject, code))
            row.add_widget(edit_btn)
            
            # Delete button
            delete_btn = Button(
                text='X',
                size_hint_x=0.15,
                background_color=(0.9, 0.3, 0.3, 1),
                color=(1, 1, 1, 1),
                font_size=15,
                bold=True
            )
            delete_btn.bind(on_press=partial(self.delete_subject, code))
            row.add_widget(delete_btn)
            
            self.list_grid.add_widget(row)
    
    def _update_row_rect(self, instance, value):
        if hasattr(instance, 'rect'):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
    
    def save_subject(self, instance):
        code = self.code_input.text.strip().upper()
        name = self.name_input.text.strip()
        credit_text = self.credit_input.text.strip()
        
        if not code:
            self.show_popup('Error', 'Please enter subject code', '❌')
            return
        
        if not name:
            self.show_popup('Error', 'Please enter subject name', '❌')
            return
        
        if not credit_text:
            self.show_popup('Error', 'Please enter credit hours', '❌')
            return
        
        try:
            credit = int(credit_text)
            if credit < 1 or credit > 6:
                self.show_popup('Error', 'Credits must be between 1 and 6', '❌')
                return
        except ValueError:
            self.show_popup('Error', 'Invalid credit hours', '❌')
            return
        
        # Check if editing or adding
        if self.current_edit_code:
            # Update existing
            if SubjectDatabase.update_subject(code, name, credit):
                self.show_toast(f'✅ Subject {code} updated')
                self.clear_form()
                self.refresh_list()
                # Update home screen footer if exists
                if hasattr(self.manager, 'get_screen') and 'home' in self.manager.screen_names:
                    home = self.manager.get_screen('home')
                    if hasattr(home, 'footer'):
                        home.footer.text = f'Subjects: {SubjectDatabase.get_subject_count()} | UMPSA Electrical Engineering'
            else:
                self.show_popup('Error', 'Subject not found', '❌')
        else:
            # Add new
            if SubjectDatabase.add_subject(code, name, credit):
                self.show_toast(f'✅ Subject {code} added')
                self.clear_form()
                self.refresh_list()
                # Update home screen footer
                if hasattr(self.manager, 'get_screen') and 'home' in self.manager.screen_names:
                    home = self.manager.get_screen('home')
                    if hasattr(home, 'footer'):
                        home.footer.text = f'Subjects: {SubjectDatabase.get_subject_count()} | UMPSA Electrical Engineering'
            else:
                self.show_popup('Error', f'Subject {code} already exists', '❌')
    
    def edit_subject(self, code, instance):
        subjects = SubjectDatabase.get_all_subjects()
        if code in subjects:
            name, credit = subjects[code]
            self.code_input.text = code
            self.name_input.text = name
            self.credit_input.text = str(credit)
            self.form_title.text = f'Edit Subject: {code}'
            self.save_btn.text = 'Update Subject'
            self.save_btn.button_color = (0.9, 0.6, 0.2, 1)  # Orange
            self.current_edit_code = code
            self.cancel_btn.opacity = 1
            self.cancel_btn.disabled = False
    
    def cancel_edit(self, instance):
        self.clear_form()
    
    def clear_form(self):
        self.code_input.text = ''
        self.name_input.text = ''
        self.credit_input.text = ''
        self.form_title.text = 'Add New Subject'
        self.save_btn.text = 'Add Subject'
        self.save_btn.button_color = (0.2, 0.7, 0.3, 1)  # Green
        self.current_edit_code = None
        self.cancel_btn.opacity = 0
        self.cancel_btn.disabled = True
    
    def delete_subject(self, code, instance):
        # Confirmation popup
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=f"Delete subject {code}?\n\nThis cannot be undone.",
            halign='center',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14
        )
        popup_layout.add_widget(content_label)
        
        btn_layout = BoxLayout(spacing=10, size_hint_y=None, height=50)
        
        confirm_btn = ModernButton(
            text='Delete',
            color=(0.9, 0.3, 0.3, 1),
            height=45
        )
        
        cancel_btn = ModernButton(
            text='Cancel',
            color=(0.5, 0.5, 0.5, 1),
            height=45
        )
        
        popup = Popup(
            title='Confirm Delete',
            content=popup_layout,
            size_hint=(0.85, 0.35),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        
        def do_delete(btn):
            if SubjectDatabase.delete_subject(code):
                self.show_toast(f'✅ Subject {code} deleted')
                self.refresh_list()
                if hasattr(self.manager, 'get_screen') and 'home' in self.manager.screen_names:
                    home = self.manager.get_screen('home')
                    if hasattr(home, 'footer'):
                        home.footer.text = f'Subjects: {SubjectDatabase.get_subject_count()} | UMPSA Electrical Engineering'
                popup.dismiss()
                self.clear_form()
        
        confirm_btn.bind(on_press=do_delete)
        cancel_btn.bind(on_press=popup.dismiss)
        
        btn_layout.add_widget(confirm_btn)
        btn_layout.add_widget(cancel_btn)
        popup_layout.add_widget(btn_layout)
        popup.open()
    
    def show_popup(self, title, content, icon="❌"):
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=content, 
            halign='center',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14
        )
        popup_layout.add_widget(content_label)
        
        btn = ModernButton(
            text='OK', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.85, 0.35),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn)
        popup.open()
    
    def show_toast(self, message):
        popup = Popup(
            title='',
            content=Label(text=message, color=(0.1, 0.1, 0.1, 1)),
            size_hint=(0.8, 0.15),
            background_color=(0.9, 0.9, 0.9, 1)
        )
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        popup.open()


class SavedDataScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.store = JsonStore('pngk_data.json') if os.path.exists('pngk_data.json') else None
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Saved Data', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Data display
        scroll = ScrollView(do_scroll_x=False, bar_width=3)
        self.data_grid = GridLayout(cols=1, spacing=5, size_hint_y=None, padding=[5, 5])
        self.data_grid.bind(minimum_height=self.data_grid.setter('height'))
        scroll.add_widget(self.data_grid)
        main_layout.add_widget(scroll)
        
        # Load data
        self.load_data()
        
        self.add_widget(main_layout)
    
    def load_data(self):
        self.data_grid.clear_widgets()
        
        if not self.store or not self.store.keys():
            label = Label(
                text='No saved data found',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=50,
                font_size=16
            )
            self.data_grid.add_widget(label)
            return
        
        # Load and display data
        try:
            for key in sorted(self.store.keys(), key=lambda x: int(x) if x.isdigit() else 0):
                data = self.store.get(key)
                subjects = data.get('subjects', [])
                
                sem_label = Label(
                    text=f"Semester {key} - {len(subjects)} subjects",
                    bold=True,
                    size_hint_y=None,
                    height=35,
                    color=(0.1, 0.3, 0.6, 1),
                    font_size=15,
                    text_size=(350, None),
                    halign='left'
                )
                self.data_grid.add_widget(sem_label)
                
                # Create a box for semester subjects
                sem_box = BoxLayout(orientation='vertical', size_hint_y=None)
                sem_box.height = len(subjects) * 28 + 10
                
                for subject in subjects:
                    text = f"  - {subject['code']} : {subject['grade']} ({subject['grade_point']:.2f})"
                    label = Label(
                        text=text,
                        size_hint_y=None,
                        height=25,
                        color=(0.2, 0.2, 0.2, 1),
                        font_size=13,
                        text_size=(350, None),
                        halign='left'
                    )
                    sem_box.add_widget(label)
                
                self.data_grid.add_widget(sem_box)
                
                # Add spacer
                spacer = Label(size_hint_y=None, height=5)
                self.data_grid.add_widget(spacer)
        except Exception as e:
            label = Label(
                text=f'Error loading data: {e}',
                color=(1, 0.3, 0.3, 1),
                size_hint_y=None,
                height=40,
                font_size=14
            )
            self.data_grid.add_widget(label)


class ImportCSVScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        
        # Back button and header
        top_bar = BoxLayout(size_hint_y=0.06, spacing=10)
        back_btn = Button(
            text='Back', 
            size_hint_x=0.25, 
            background_color=(0.15, 0.15, 0.15, 1),
            color=(1, 1, 1, 1),
            font_size=14,
            bold=True
        )
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='Import CSV', font_size=20, bold=True, color=(0.1, 0.3, 0.6, 1)))
        main_layout.add_widget(top_bar)
        
        # Instructions
        instructions = Label(
            text="""CSV Import Instructions:

1. Create a CSV file with columns:
   subject_code, grade, semester

2. Example:
   BEL1113, A, 1
   BEL1233, B+, 1

3. Place CSV in:
   /storage/emulated/0/Download/

4. Valid grades: A, A-, B+, B, B-, 
   C+, C, C-, D+, D, E, F, HL, HG

5. Unknown subjects will be auto-created
   with credits from the last digit""",
            halign='left',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=0.6,
            font_size=13,
            text_size=(350, None)
        )
        main_layout.add_widget(instructions)
        
        # Import button
        import_btn = ModernButton(
            text='Import CSV File', 
            color=(0.2, 0.5, 0.9, 1),
            height=50
        )
        import_btn.bind(on_press=self.import_csv)
        main_layout.add_widget(import_btn)
        
        # Status
        self.status_label = Label(
            text='',
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=0.05,
            font_size=14
        )
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def import_csv(self, instance):
        self.status_label.text = 'Looking for CSV file...'
        
        # Try to find CSV in common locations
        possible_paths = [
            '/storage/emulated/0/Download/',
            '/sdcard/Download/',
            '/sdcard/',
            './'
        ]
        
        found_file = None
        for path in possible_paths:
            try:
                if os.path.exists(path):
                    for file in os.listdir(path):
                        if file.endswith('.csv'):
                            found_file = os.path.join(path, file)
                            break
                if found_file:
                    break
            except:
                continue
        
        if not found_file:
            self.status_label.text = 'No CSV file found'
            self.show_popup('Error', 'Please place your CSV file in the Downloads folder and try again.', '❌')
            return
        
        # Parse CSV
        try:
            results = []
            with open(found_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                if not header:
                    self.show_popup('Error', 'Empty CSV file', '❌')
                    return
                
                for row in reader:
                    if not row or not row[0].strip() or row[0].strip().startswith('#'):
                        continue
                    
                    if len(row) < 2:
                        continue
                    
                    code = row[0].strip().upper()
                    grade_letter = row[1].strip().upper()
                    semester = int(row[2].strip()) if len(row) >= 3 and row[2].strip() else 0
                    
                    if not GradeDatabase.is_valid_grade(grade_letter):
                        continue
                    
                    subject = SubjectDatabase.get_subject(code)
                    grade = Grade(grade_letter, GradeDatabase.get_grade_point(grade_letter))
                    results.append(SubjectResult(subject, grade, semester))
            
            if not results:
                self.status_label.text = 'No valid data found'
                self.show_popup('Error', 'No valid subject-grade entries found in CSV', '❌')
                return
            
            # Save results
            store = JsonStore('pngk_data.json')
            semester_data = {}
            
            for result in results:
                sem = str(result.semester)
                if sem not in semester_data:
                    semester_data[sem] = []
                semester_data[sem].append({
                    'code': result.subject.code,
                    'grade': result.grade.letter,
                    'grade_point': result.grade.grade_point
                })
            
            # Save to store
            for sem, subjects in semester_data.items():
                store.put(sem, subjects=subjects)
            
            # Calculate PNGK
            total_points, total_credits, pngk, _ = PNGCalculator.calculate_pngk(results)
            classification, icon = PNGCalculator.get_classification(pngk)
            
            self.status_label.text = f'Imported {len(results)} subjects'
            self.show_popup(
                'Import Successful',
                f"{icon} {len(results)} subjects imported\n"
                f"PNGK: {pngk:.3f}\n"
                f"{classification}",
                icon
            )
            
        except Exception as e:
            self.status_label.text = f'Error: {str(e)}'
            self.show_popup('Error', f'Failed to import CSV:\n{str(e)}', '❌')
    
    def show_popup(self, title, content, icon="📁"):
        popup_layout = BoxLayout(orientation='vertical', padding=[15, 20], spacing=15)
        
        content_label = Label(
            text=content, 
            halign='left',
            color=(0.1, 0.1, 0.1, 1),
            font_size=14,
            text_size=(300, None)
        )
        popup_layout.add_widget(content_label)
        
        btn = ModernButton(
            text='Close', 
            color=(0.2, 0.5, 0.9, 1),
            height=45
        )
        popup = Popup(
            title=title, 
            content=popup_layout, 
            size_hint=(0.85, 0.5),
            background_color=(1, 1, 1, 1),
            title_color=(0.1, 0.3, 0.6, 1),
            title_size=18
        )
        btn.bind(on_press=popup.dismiss)
        popup_layout.add_widget(btn)
        popup.open()


# ==================== MAIN APP ====================

class PNGSimulatorApp(App):
    def build(self):
        # Set app theme
        Window.clearcolor = (0.95, 0.95, 0.98, 1)
        
        # Initialize database
        SubjectDatabase.load_from_store()
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(PNGCalculatorScreen(name='png_calculator'))
        sm.add_widget(PNGKCalculatorScreen(name='pngk_calculator'))
        sm.add_widget(TargetCalculatorScreen(name='target_calculator'))
        sm.add_widget(SubjectDatabaseScreen(name='subject_database'))
        sm.add_widget(ManageDatabaseScreen(name='manage_database'))
        sm.add_widget(SavedDataScreen(name='saved_data'))
        sm.add_widget(ImportCSVScreen(name='import_csv'))
        
        return sm
    
    def on_start(self):
        # Create data directories if needed
        try:
            if not os.path.exists('pngk_data.json'):
                JsonStore('pngk_data.json')
            if not os.path.exists('subjects_db.json'):
                JsonStore('subjects_db.json')
        except:
            pass


# ==================== MAIN ENTRY ====================

if __name__ == '__main__':
    PNGSimulatorApp().run()
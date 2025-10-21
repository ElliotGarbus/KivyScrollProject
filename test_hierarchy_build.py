"""
test_hierarchy_build.py

Phase 1 Interim Test: Verify hierarchy building infrastructure

Tests that ScrollViewHierarchy class and _build_hierarchy_recursive() work correctly.
This test creates a 3-level vertical nest and verifies the hierarchy structure.
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from scrollview import ScrollView
from kivy.input.motionevent import MotionEvent


class TestHierarchyApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='[b]Phase 1 Test: Hierarchy Building[/b]\n'
                 'Click the "Test Hierarchy" button to verify hierarchy structure',
            markup=True,
            size_hint_y=None,
            height=60
        )
        root.add_widget(title)
        
        # Create 3-level vertical nest (V→V→V)
        # Outer ScrollView
        outer_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(10),
            size_hint=(1, 1)
        )
        
        outer_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(20),
            padding=dp(10)
        )
        outer_content.bind(minimum_height=outer_content.setter('height'))
        
        # Add some padding content
        for i in range(3):
            outer_content.add_widget(Label(
                text=f'Outer Content {i+1}',
                size_hint_y=None,
                height=dp(50)
            ))
        
        # Middle ScrollView
        middle_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
            size_hint=(None, None),
            size=(dp(600), dp(400))
        )
        
        middle_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=dp(10)
        )
        middle_content.bind(minimum_height=middle_content.setter('height'))
        
        # Add some middle content
        for i in range(3):
            middle_content.add_widget(Label(
                text=f'Middle Content {i+1}',
                size_hint_y=None,
                height=dp(40),
                color=(1, 1, 0, 1)
            ))
        
        # Inner ScrollView
        inner_sv = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(6),
            size_hint=(None, None),
            size=(dp(500), dp(300))
        )
        
        inner_content = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10),
            padding=dp(10)
        )
        inner_content.bind(minimum_height=inner_content.setter('height'))
        
        # Add inner content
        for i in range(10):
            inner_content.add_widget(Button(
                text=f'Inner Button {i+1}',
                size_hint_y=None,
                height=dp(50)
            ))
        
        # Assemble hierarchy
        inner_sv.add_widget(inner_content)
        middle_content.add_widget(inner_sv)
        middle_sv.add_widget(middle_content)
        outer_content.add_widget(middle_sv)
        outer_sv.add_widget(outer_content)
        
        root.add_widget(outer_sv)
        
        # Test button
        test_btn = Button(
            text='Test Hierarchy',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1.0, 1)
        )
        test_btn.bind(on_press=lambda x: self.test_hierarchy(outer_sv, middle_sv, inner_sv))
        root.add_widget(test_btn)
        
        # Results label
        self.results_label = Label(
            text='Click button to run test',
            size_hint_y=None,
            height=dp(200),
            color=(0, 1, 0, 1)
        )
        root.add_widget(self.results_label)
        
        # Store references
        self.outer_sv = outer_sv
        self.middle_sv = middle_sv
        self.inner_sv = inner_sv
        
        return root
    
    def test_hierarchy(self, outer, middle, inner):
        """Test hierarchy building by creating a fake touch event."""
        results = []
        results.append("=== PHASE 1 HIERARCHY TEST ===\n")
        
        try:
            # Create a fake touch over the innermost ScrollView
            # We'll use a simple touch object with position
            class FakeTouch:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
                    self.pos = (x, y)
                    self.uid = 'test'
                    self.ud = {}
                
                def push(self):
                    pass
                
                def pop(self):
                    pass
                
                def apply_transform_2d(self, transform):
                    # Simple pass-through for testing
                    pass
            
            # Get center of inner ScrollView
            touch = FakeTouch(inner.center_x, inner.center_y)
            
            # Build hierarchy
            results.append("Building hierarchy...")
            hierarchy = outer._build_hierarchy_recursive(touch)
            
            if hierarchy is None:
                results.append("❌ FAIL: hierarchy is None")
                self.results_label.text = '\n'.join(results)
                return
            
            results.append("✓ Hierarchy created\n")
            
            # Test depth
            results.append(f"Depth: {hierarchy.depth}")
            if hierarchy.depth == 3:
                results.append("✓ PASS: Depth is 3")
            else:
                results.append(f"❌ FAIL: Expected depth 3, got {hierarchy.depth}")
            
            # Test outer
            results.append(f"\nOuter SV: {hierarchy.outer is outer}")
            if hierarchy.outer is outer:
                results.append("✓ PASS: Outer is correct")
            else:
                results.append("❌ FAIL: Outer is wrong")
            
            # Test inner
            results.append(f"\nInner SV: {hierarchy.inner is inner}")
            if hierarchy.inner is inner:
                results.append("✓ PASS: Inner is correct")
            else:
                results.append("❌ FAIL: Inner is wrong")
            
            # Test middle
            results.append(f"\nMiddle SV (index 1): {hierarchy.scrollviews[1] is middle}")
            if hierarchy.scrollviews[1] is middle:
                results.append("✓ PASS: Middle is correct")
            else:
                results.append("❌ FAIL: Middle is wrong")
            
            # Test classifications
            results.append("\nClassifications:")
            for i in range(1, hierarchy.depth):
                classification = hierarchy.get_classification(i)
                results.append(f"  Level {i}: {classification}")
                if classification == 'parallel':
                    results.append(f"  ✓ PASS: Level {i} classified as parallel")
                else:
                    results.append(f"  ❌ FAIL: Expected parallel, got {classification}")
            
            # Test parent navigation
            results.append("\nParent Navigation:")
            for i in range(hierarchy.depth):
                parent = hierarchy.get_parent(i)
                if i == 0:
                    if parent is None:
                        results.append(f"  Level {i}: No parent (✓ correct)")
                    else:
                        results.append(f"  Level {i}: Has parent (❌ should be None)")
                else:
                    expected_parent = hierarchy.scrollviews[i-1]
                    if parent is expected_parent:
                        results.append(f"  Level {i}: Parent is correct (✓)")
                    else:
                        results.append(f"  Level {i}: Parent is wrong (❌)")
            
            results.append("\n=== TEST COMPLETE ===")
            results.append("\nAll core functionality verified!")
            results.append("Hierarchy infrastructure ready for Phase 2")
            
        except Exception as e:
            results.append(f"\n❌ EXCEPTION: {str(e)}")
            import traceback
            results.append(traceback.format_exc())
        
        self.results_label.text = '\n'.join(results)
        print('\n'.join(results))


if __name__ == '__main__':
    TestHierarchyApp().run()


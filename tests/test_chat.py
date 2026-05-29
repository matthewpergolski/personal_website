#!/usr/bin/env python3

# Test script to debug ChatWidget rendering - let's isolate the issue
import sys
sys.path.insert(0, 'src')

from components.chat.widget import ChatWidget
from fasthtml.common import Div, Button, Script, Style

print("🔍 DIAGNOSTIC ChatWidget TEST")
print("============================")

try:
    # Create minimal test components
    print("\\n🔧 Testing minimal FastHTML components:")

    # Test if basic Div works
    test_div = Div("Test content", id="test-div")
    print(f"✓ Basic Div: {type(test_div)} -> {str(test_div)[:50]}...")

    # Test if Button works
    test_btn = Button("Test", id="test-btn", cls="test-btn")
    print(f"✓ Basic Button: {type(test_btn)} -> {str(test_btn)[:50]}...")

    # Test if Script/Style work
    test_script = Script("console.log('test');")
    print(f"✓ Basic Script: {type(test_script)} -> {str(test_script)[:50]}...")

    print("\\n🌐 Testing ChatWidget components:")

    # Test creating ChatWidget
    chat = ChatWidget.professional_mode()
    print("✓ ChatWidget instance created")

    # Test individual methods - these should return proper FastHTML components
    container = chat._render_chat_container()
    print(f"✓ _render_chat_container: {type(container)} -> {len(str(container))} chars")
    print(f"  → Preview: {str(container)[:70]}...")

    toggle = chat._render_toggle_button()
    print(f"✓ _render_toggle_button: {type(toggle)} -> {len(str(toggle))} chars")
    print(f"  → Preview: {str(toggle)[:70]}...")

    # Let's test the Style and Script separately
    styles_component = chat._render_styles()
    print(f"✓ _render_styles: {type(styles_component)} -> {len(str(styles_component))} chars")

    scripts_component = chat._render_scripts()
    print(f"✓ _render_scripts: {type(scripts_component)} -> {len(str(scripts_component))} chars")

    # Now test the main render method
    print("\\n🎯 Testing main render() method:")
    render_result = chat.render()
    print(f"✓ render(): {type(render_result)} -> {len(str(render_result))} chars")
    print(f"✓ Render result: {str(render_result)[:150]}...")

    # Check for expected structure
    full_render = str(render_result)

    print("\\n📊 Analysis:")
    print(f"✓ Total length: {len(full_render)} characters")
    print(f"✓ Contains 'chat-widget': {'chat-widget' in full_render}")
    print(f"✓ Contains 'toggleChatWidget': {'toggleChatWidget' in full_render}")

    if len(full_render) < 100:
        print("\\n❌ ISSUE: Render is too short - something's wrong with the widget structure")
    else:
        print("\\n✅ ChatWidget appears to be rendering correctly!")

except Exception as e:
    import traceback
    print(f"\\n❌ ERROR: {e}")
    print("Full traceback:")
    traceback.print_exc()

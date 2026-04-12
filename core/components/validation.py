import flet as ft
from core.theme import theme_colors
from core.components.common import ValidationService


def validate_field_on_blur(field_ref, error_text_ref, validator_func, *args):
    """
    Creates an on_blur handler for a field that validates it and shows/hides error text
    
    Args:
        field_ref: Reference to the TextField to validate
        error_text_ref: Reference to the Text to show error messages
        validator_func: Function that takes field value and returns (is_valid, error_message)
        *args: Additional arguments to pass to validator_func
    """
    def on_blur(e):
        is_valid, error_msg = validator_func(field_ref.value, *args)
        error_text_ref.visible = not is_valid
        error_text_ref.value = error_msg or ""
        
        # Update field appearance
        if is_valid:
            field_ref.border_color = theme_colors(getattr(field_ref, 'dark_mode', True))["input_border"]
            field_ref.error_text = ""
        else:
            field_ref.border_color = ft.Colors.RED_400
            field_ref.error_text = error_msg or "Campo inválido"
            
        field_ref.update()
        error_text_ref.update()
        
    return on_blur


def create_validated_field(label, value="", validator=None, max_length=None, 
                          input_filter=None, expand=False, width=None, dark_mode=True):
    """
    Creates a TextField with built-in validation support
    
    Returns:
        tuple: (TextField, error_text, on_blur_handler)
    """
    tc = theme_colors(dark_mode)
    
    field = ft.TextField(
        label=label,
        value=value,
        max_length=max_length,
        input_filter=input_filter,
        expand=expand,
        width=width,
        border_radius=8,
        filled=True,
        bgcolor=tc["input_bg"],
        border_color=tc["input_border"],
        color=tc["input_text"],
        label_style=ft.TextStyle(color=tc["input_label"]),
    )
    
    error_text = ft.Text("", color=ft.Colors.RED_400, size=12, visible=False)
    
    # Store dark_mode for validation function
    field.dark_mode = dark_mode
    
    return field, error_text


class FormValidationService:
    """Service for validating entire forms"""
    
    @staticmethod
    def validate_form(fields_validators):
        """
        Validates multiple fields
        
        Args:
            fields_validators: List of tuples (field_value, validator_func, *args)
            
        Returns:
            tuple: (is_valid, error_message)
        """
        for field_value, validator_func, *args in fields_validators:
            is_valid, error_msg = validator_func(field_value, *args)
            if not is_valid:
                return False, error_msg
        return True, None
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from users.models import User


class Roadmap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    domain = models.CharField(max_length=100, help_text="e.g., 'Python', 'Blockchain'")
    modules = models.JSONField(default=list, help_text="Array of {name: String, resources: Array<URL>, estimated_time: Integer, completed: Boolean}")
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Progress percentage (0-100)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmaps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'domain']),
            models.Index(fields=['progress']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.email}'s {self.domain} Roadmap"

    def clean(self):
        """Validate roadmap data."""
        super().clean()

        # Validate domain
        if self.domain:
            self.domain = self.domain.strip()
            if len(self.domain) < 2:
                raise ValidationError({'domain': 'Domain must be at least 2 characters long'})

        # Validate modules structure
        if self.modules:
            self._validate_modules()

        # Validate progress
        if not (0 <= self.progress <= 100):
            raise ValidationError({'progress': 'Progress must be between 0 and 100'})

    def _validate_modules(self):
        """Validate modules JSON structure."""
        if not isinstance(self.modules, list):
            raise ValidationError({'modules': 'Modules must be a list'})

        if len(self.modules) > 20:
            raise ValidationError({'modules': 'Maximum 20 modules allowed'})

        for i, module in enumerate(self.modules):
            if not isinstance(module, dict):
                raise ValidationError({f'modules[{i}]': 'Each module must be a dictionary'})

            required_fields = ['name', 'resources', 'estimated_time', 'completed']
            for field in required_fields:
                if field not in module:
                    raise ValidationError({f'modules[{i}].{field}': f'Module missing required field: {field}'})

            # Validate name
            if not isinstance(module['name'], str) or len(module['name'].strip()) < 3:
                raise ValidationError({f'modules[{i}].name': 'Module name must be at least 3 characters'})

            # Validate resources
            if not isinstance(module['resources'], list):
                raise ValidationError({f'modules[{i}].resources': 'Resources must be a list'})

            # Validate estimated_time
            if not isinstance(module['estimated_time'], (int, float)) or module['estimated_time'] <= 0:
                raise ValidationError({f'modules[{i}].estimated_time': 'Estimated time must be a positive number'})

            # Validate completed
            if not isinstance(module['completed'], bool):
                raise ValidationError({f'modules[{i}].completed': 'Completed must be a boolean'})

    def calculate_progress(self):
        """
        Calculate progress based on completed modules.
        Returns the calculated progress percentage.
        """
        if not self.modules:
            return 0.0

        completed_modules = sum(1 for module in self.modules if module.get('completed', False))
        total_modules = len(self.modules)

        if total_modules == 0:
            return 0.0

        calculated_progress = (completed_modules / total_modules) * 100
        return round(calculated_progress, 2)

    def complete_module(self, module_index):
        """
        Mark a specific module as completed and update progress.
        """
        if not (0 <= module_index < len(self.modules)):
            raise ValueError(f"Module index {module_index} is out of range")

        self.modules[module_index]['completed'] = True
        self.progress = self.calculate_progress()
        self.save()

        return self.progress

    def get_total_estimated_time(self):
        """Get total estimated time for all modules in hours."""
        if not self.modules:
            return 0

        return sum(module.get('estimated_time', 0) for module in self.modules)

    def get_completed_modules_count(self):
        """Get count of completed modules."""
        if not self.modules:
            return 0

        return sum(1 for module in self.modules if module.get('completed', False))

    def get_remaining_modules(self):
        """Get list of remaining (incomplete) modules."""
        if not self.modules:
            return []

        return [module for module in self.modules if not module.get('completed', False)]

    def is_completed(self):
        """Check if roadmap is fully completed."""
        return self.progress >= 100.0

    def get_completion_percentage(self):
        """Get completion percentage (same as progress field)."""
        return self.progress

    def get_module_by_index(self, index):
        """Get module by index."""
        if not (0 <= index < len(self.modules)):
            return None
        return self.modules[index]

    def update_module_progress(self, module_index, completed):
        """Update a specific module's completion status."""
        if not (0 <= module_index < len(self.modules)):
            raise ValueError(f"Module index {module_index} is out of range")

        self.modules[module_index]['completed'] = bool(completed)
        self.progress = self.calculate_progress()
        self.save()

        return self.progress

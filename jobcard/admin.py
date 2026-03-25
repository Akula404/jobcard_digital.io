from django.contrib import admin
from .models import JobCard, TempSubmission, ShiftSubmission


# =====================================================
# JOBCARD ADMIN
# =====================================================
@admin.register(JobCard)
class JobCardAdmin(admin.ModelAdmin):

    list_display = (
        'date', 'line', 'shift',
        'wo_number',
        'product_name',
        'target_quantity',
        'total_output_display'
    )

    list_filter = ('line', 'shift', 'date')

    search_fields = (
        'wo_number',
        'product_code',
        'product_name',
        'operator_names',
        'supervisor_names'
    )

    ordering = ('-date',)

    readonly_fields = ('total_output_display',)

    fieldsets = (
        ('Job Details', {
            'fields': (
                'date', 'line', 'shift',
                'wo_number',
                'product_code', 'product_name',
                'target_quantity'
            )
        }),

        ('Hourly Output', {
            'fields': (
                'hour1', 'hour2', 'hour3', 'hour4', 'hour5',
                'hour6', 'hour7', 'hour8', 'hour9', 'hour10', 'hour11', 'hour12',
                'total_output_display'
            )
        }),

        ('Damages / Rejects', {
            'fields': (
                'jar', 'cap', 'front_label', 'back_label',
                'carton', 'sleeve', 'sticker',
                'tube', 'packets',
                'roll_on_ball', 'jar_pump'
            )
        }),

        ('Operators / Supervisors', {
            'fields': (
                'operator_names',
                'supervisor_names',
                'line_captain_signature',
                'supervisor_signature'
            )
        }),
    )

    def total_output_display(self, obj):
        return obj.total_output()
    total_output_display.short_description = "Total Output"



# =====================================================
# TEMP SUBMISSION ADMIN (REALTIME DATA)
# =====================================================
@admin.register(TempSubmission)
class TempSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        'operator',
        'date',
        'line',
        'shift',
        'total_output_display',
        'updated_at'
    )

    list_filter = ('date', 'line', 'shift')

    ordering = ('-updated_at',)

    readonly_fields = ('updated_at', 'total_output_display')

    def total_output_display(self, obj):
        return obj.total_output()
    total_output_display.short_description = "Live Total"



# =====================================================
# SHIFT SUBMISSION ADMIN (FINALIZED SHIFTS)
# =====================================================
@admin.register(ShiftSubmission)
class ShiftSubmissionAdmin(admin.ModelAdmin):

    list_display = (
        'date',
        'line',
        'shift',
        'supervisor_approved',
        'created_at'
    )

    list_filter = ('date', 'line', 'shift', 'supervisor_approved')

    ordering = ('-date', '-created_at')

    readonly_fields = ('aggregated_data', 'created_at')

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# -----------------------------
# CHOICES
# -----------------------------
LINE_CHOICES = [
    ('FL001', 'FL 001'),
    ('FL006', 'FL 006'),
    ('FL007', 'FL 007'),
    ('FL008', 'FL 008'),
    ('FL009', 'FL 009'),
    ('FL010', 'FL 010'),
    ('FL013', 'FL 013'),
    ('FL014', 'FL 014'),
    ('COPACK', 'CO-PACKING'),
]

SHIFT_CHOICES = [
    ('Day', 'Day Shift'),
    ('Night', 'Night Shift'),
]

# =====================================================
# FINAL JOBCARD (Permanent Record)
# =====================================================
class JobCard(models.Model):
    date = models.DateField(default=timezone.localdate, db_index=True)
    line = models.CharField(max_length=10, choices=LINE_CHOICES, db_index=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, db_index=True)

    wo_number = models.CharField(max_length=50)
    product_code = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    target_quantity = models.PositiveIntegerField(default=0)

    is_submitted = models.BooleanField(default=False)

    hour1 = models.PositiveIntegerField(default=0)
    hour2 = models.PositiveIntegerField(default=0)
    hour3 = models.PositiveIntegerField(default=0)
    hour4 = models.PositiveIntegerField(default=0)
    hour5 = models.PositiveIntegerField(default=0)
    hour6 = models.PositiveIntegerField(default=0)
    hour7 = models.PositiveIntegerField(default=0)
    hour8 = models.PositiveIntegerField(default=0)
    hour9 = models.PositiveIntegerField(default=0)
    hour10 = models.PositiveIntegerField(default=0)
    hour11 = models.PositiveIntegerField(default=0)
    hour12 = models.PositiveIntegerField(default=0)

    jar_damage = models.PositiveIntegerField(default=0)
    cap_damage = models.PositiveIntegerField(default=0)
    front_label_damage = models.PositiveIntegerField(default=0)
    back_label_damage = models.PositiveIntegerField(default=0)
    carton_damage = models.PositiveIntegerField(default=0)
    sleeve_damage = models.PositiveIntegerField(default=0)
    sticker_damage = models.PositiveIntegerField(default=0)
    tube_damage = models.PositiveIntegerField(default=0)
    packets_damage = models.PositiveIntegerField(default=0)
    roll_on_ball_damage = models.PositiveIntegerField(default=0)
    jar_pump_damage = models.PositiveIntegerField(default=0)

    jar_reject = models.PositiveIntegerField(default=0)
    cap_reject = models.PositiveIntegerField(default=0)
    front_label_reject = models.PositiveIntegerField(default=0)
    back_label_reject = models.PositiveIntegerField(default=0)
    carton_reject = models.PositiveIntegerField(default=0)
    sleeve_reject = models.PositiveIntegerField(default=0)
    sticker_reject = models.PositiveIntegerField(default=0)
    tube_reject = models.PositiveIntegerField(default=0)
    packets_reject = models.PositiveIntegerField(default=0)
    roll_on_ball_reject = models.PositiveIntegerField(default=0)
    jar_pump_reject = models.PositiveIntegerField(default=0)

    operator_names = models.TextField()
    supervisor_names = models.TextField()
    line_captain_signature = models.CharField(max_length=100)
    supervisor_signature = models.CharField(max_length=100)

    # ✅ FIX: Normalize FL015 → FL014
    def save(self, *args, **kwargs):
        if self.line == "FL015":
            self.line = "FL014"
        super().save(*args, **kwargs)

    def total_output(self):
        return sum([
            self.hour1, self.hour2, self.hour3, self.hour4, self.hour5,
            self.hour6, self.hour7, self.hour8, self.hour9, self.hour10,
            self.hour11, self.hour12
        ])
    
    def total_damage(self):
        return sum([
            self.jar_damage, self.cap_damage, self.front_label_damage,
            self.back_label_damage, self.carton_damage, self.sleeve_damage,
            self.sticker_damage, self.tube_damage, self.packets_damage,
            self.roll_on_ball_damage, self.jar_pump_damage
        ])

    def total_reject(self):
        return sum([
            self.jar_reject, self.cap_reject, self.front_label_reject,
            self.back_label_reject, self.carton_reject, self.sleeve_reject,
            self.sticker_reject, self.tube_reject, self.packets_reject,
            self.roll_on_ball_reject, self.jar_pump_reject
        ])

    def efficiency(self):
        if self.target_quantity == 0:
            return 0
        return round((self.total_output() / self.target_quantity) * 100, 1)

    class Meta:
        ordering = ["-date", "line"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "line", "shift", "wo_number"],
                name="unique_jobcard_per_wo_per_shift"
            )
        ]
        indexes = [
            models.Index(fields=["date", "line", "shift"]),
        ]

    def __str__(self):
        return f"{self.date} | {self.product_name} | {self.line} | {self.shift}"


# =====================================================
# LIVE OPERATOR ENTRY (REALTIME TABLE)
# =====================================================
class TempSubmission(models.Model):
    operator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.localdate, db_index=True)
    line = models.CharField(max_length=10, choices=LINE_CHOICES, db_index=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, db_index=True)

    hour1 = models.PositiveIntegerField(default=0)
    hour2 = models.PositiveIntegerField(default=0)
    hour3 = models.PositiveIntegerField(default=0)
    hour4 = models.PositiveIntegerField(default=0)
    hour5 = models.PositiveIntegerField(default=0)
    hour6 = models.PositiveIntegerField(default=0)
    hour7 = models.PositiveIntegerField(default=0)
    hour8 = models.PositiveIntegerField(default=0)
    hour9 = models.PositiveIntegerField(default=0)
    hour10 = models.PositiveIntegerField(default=0)
    hour11 = models.PositiveIntegerField(default=0)
    hour12 = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    # ✅ FIX: Normalize FL015 → FL014
    def save(self, *args, **kwargs):
        if self.line == "FL015":
            self.line = "FL014"
        super().save(*args, **kwargs)

    def total_output(self):
        return sum([
            self.hour1, self.hour2, self.hour3, self.hour4, self.hour5,
            self.hour6, self.hour7, self.hour8, self.hour9, self.hour10,
            self.hour11, self.hour12
        ])

    class Meta:
        ordering = ["line", "shift"]
        constraints = [
            models.UniqueConstraint(
                fields=["operator", "date", "line", "shift"],
                name="unique_operator_submission"
            )
        ]
        indexes = [
            models.Index(fields=["date", "shift", "line"]),
        ]

    def __str__(self):
        name = self.operator.username if self.operator else "Anonymous"
        return f"{name} | {self.date} | {self.shift} | {self.line}"


# =====================================================
# SHIFT FINAL SNAPSHOT (Audit + History Table)
# =====================================================
class ShiftSubmission(models.Model):
    date = models.DateField(db_index=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, db_index=True)
    line = models.CharField(max_length=10, choices=LINE_CHOICES, db_index=True)

    aggregated_data = models.JSONField(default=list)
    supervisor_approved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ FIX: Normalize FL015 → FL014
    def save(self, *args, **kwargs):
        if self.line == "FL015":
            self.line = "FL014"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["date", "shift", "line"],
                name="unique_shift_submission"
            )
        ]

    def __str__(self):
        return f"{self.date} - {self.shift} - {self.line}"


# =====================================================
# HOUR LOCK SYSTEM
# =====================================================
class HourEntry(models.Model):
    hour = models.IntegerField()
    value = models.FloatField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.value not in [None, 0, 0.0]:
            self.is_locked = True
        super().save(*args, **kwargs)


class ActiveShift(models.Model):
    shift = models.CharField(max_length=10)
    date = models.DateField()
    last_reset = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.shift} — {self.date}"
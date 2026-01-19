from django.db import models
from django.utils import timezone
from .models import TeamMember

class EmployeeProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    team_member = models.OneToOneField(TeamMember, on_delete=models.CASCADE, related_name='hrms_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    joining_date = models.DateField(default=timezone.now)
    department = models.CharField(max_length=100, default='Sales')
    employment_type = models.CharField(max_length=20, default='Full Time')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.team_member.name} - {self.employee_id}"
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"EMP{self.team_member.id:04d}"
        super().save(*args, **kwargs)

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('holiday', 'Holiday'),
    ]
    
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team_member', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.team_member.name} - {self.date} - {self.status}"

class LeaveRequest(models.Model):
    LEAVE_TYPES = [
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('maternity', 'Maternity Leave'),
        ('paternity', 'Paternity Leave'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    from_date = models.DateField()
    to_date = models.DateField()
    days_requested = models.IntegerField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(TeamMember, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team_member.name} - {self.leave_type} - {self.from_date} to {self.to_date}"
    
    def save(self, *args, **kwargs):
        if not self.days_requested:
            self.days_requested = (self.to_date - self.from_date).days + 1
        super().save(*args, **kwargs)

class LeaveBalance(models.Model):
    team_member = models.OneToOneField(TeamMember, on_delete=models.CASCADE, related_name='leave_balance')
    annual_leave = models.IntegerField(default=21)
    sick_leave = models.IntegerField(default=12)
    personal_leave = models.IntegerField(default=5)
    emergency_leave = models.IntegerField(default=3)
    maternity_leave = models.IntegerField(default=180)
    paternity_leave = models.IntegerField(default=15)
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['team_member', 'year']
    
    def __str__(self):
        return f"{self.team_member.name} - Leave Balance {self.year}"

class Payroll(models.Model):
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='payroll_records')
    month = models.IntegerField()
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    paid_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['team_member', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.team_member.name} - {self.month}/{self.year}"
    
    def save(self, *args, **kwargs):
        self.gross_salary = (
            self.basic_salary + self.hra + self.transport_allowance + 
            self.medical_allowance + self.other_allowances
        )
        self.net_salary = (
            self.gross_salary - self.pf_deduction - 
            self.tax_deduction - self.other_deductions
        )
        super().save(*args, **kwargs)

class PerformanceReview(models.Model):
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='conducted_reviews')
    review_period_start = models.DateField()
    review_period_end = models.DateField()
    overall_rating = models.IntegerField(choices=RATING_CHOICES)
    communication_rating = models.IntegerField(choices=RATING_CHOICES)
    technical_rating = models.IntegerField(choices=RATING_CHOICES)
    teamwork_rating = models.IntegerField(choices=RATING_CHOICES)
    leadership_rating = models.IntegerField(choices=RATING_CHOICES, null=True, blank=True)
    strengths = models.TextField()
    areas_for_improvement = models.TextField()
    goals_for_next_period = models.TextField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team_member.name} - Review {self.review_period_start} to {self.review_period_end}"

class Goal(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]
    
    team_member = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.DecimalField(max_digits=10, decimal_places=2)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, default='leads')
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    created_by = models.ForeignKey(TeamMember, on_delete=models.CASCADE, related_name='created_goals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.team_member.name} - {self.title}"
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min((self.current_value / self.target_value) * 100, 100)
        return 0
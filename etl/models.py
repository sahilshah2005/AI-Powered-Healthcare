from django.db import models
from django.utils import timezone


# ============================================================
# DIMENSION TABLES — Star Schema
# ============================================================

class DimGender(models.Model):
    gender_name = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'Dimension: Gender'
        verbose_name_plural = 'Dimension: Genders'

    def __str__(self):
        return self.gender_name


class DimAgeGroup(models.Model):
    age_range = models.CharField(max_length=20, unique=True)
    min_age = models.IntegerField(default=0)
    max_age = models.IntegerField(default=999)

    class Meta:
        verbose_name = 'Dimension: Age Group'
        verbose_name_plural = 'Dimension: Age Groups'
        ordering = ['min_age']

    def __str__(self):
        return self.age_range


class DimChestPainType(models.Model):
    cp_code = models.IntegerField(unique=True, default=0)
    cp_name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Dimension: Chest Pain Type'
        verbose_name_plural = 'Dimension: Chest Pain Types'

    def __str__(self):
        return self.cp_name


class DimRestECG(models.Model):
    ecg_code = models.IntegerField(unique=True, default=0)
    ecg_result = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Dimension: Resting ECG'
        verbose_name_plural = 'Dimension: Resting ECGs'

    def __str__(self):
        return self.ecg_result


class DimCholesterolCategory(models.Model):
    category_name = models.CharField(max_length=30, unique=True)
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=9999)

    class Meta:
        verbose_name = 'Dimension: Cholesterol Category'
        verbose_name_plural = 'Dimension: Cholesterol Categories'

    def __str__(self):
        return self.category_name


class DimBPCategory(models.Model):
    category_name = models.CharField(max_length=30, unique=True)
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=9999)

    class Meta:
        verbose_name = 'Dimension: BP Category'
        verbose_name_plural = 'Dimension: BP Categories'

    def __str__(self):
        return self.category_name


class DimHeartRateCategory(models.Model):
    category_name = models.CharField(max_length=30, unique=True)
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=9999)

    class Meta:
        verbose_name = 'Dimension: Heart Rate Category'
        verbose_name_plural = 'Dimension: Heart Rate Categories'

    def __str__(self):
        return self.category_name


class DimTime(models.Model):
    etl_date = models.DateField()
    year = models.IntegerField()
    month = models.IntegerField()
    quarter = models.IntegerField()

    class Meta:
        verbose_name = 'Dimension: Time'
        verbose_name_plural = 'Dimension: Time'
        unique_together = ['etl_date']

    def __str__(self):
        return str(self.etl_date)


# ============================================================
# FACT TABLE
# ============================================================

class PatientFact(models.Model):
    # Foreign Keys to Dimensions
    gender = models.ForeignKey(DimGender, on_delete=models.CASCADE)
    age_group = models.ForeignKey(DimAgeGroup, on_delete=models.CASCADE)
    cp_type = models.ForeignKey(DimChestPainType, on_delete=models.CASCADE)
    rest_ecg = models.ForeignKey(DimRestECG, on_delete=models.CASCADE)
    chol_category = models.ForeignKey(DimCholesterolCategory, on_delete=models.CASCADE, null=True, blank=True)
    bp_category = models.ForeignKey(DimBPCategory, on_delete=models.CASCADE, null=True, blank=True)
    hr_category = models.ForeignKey(DimHeartRateCategory, on_delete=models.CASCADE, null=True, blank=True)
    etl_time = models.ForeignKey(DimTime, on_delete=models.CASCADE, null=True, blank=True)

    # Measures / Facts
    age = models.IntegerField()
    trestbps = models.FloatField(null=True, blank=True)
    chol = models.FloatField(null=True, blank=True)
    fbs = models.BooleanField(default=False)
    thalach = models.FloatField(null=True, blank=True)
    exang = models.BooleanField(default=False)
    oldpeak = models.FloatField(null=True, blank=True)
    slope = models.IntegerField(null=True, blank=True)
    ca = models.IntegerField(null=True, blank=True)
    thal = models.IntegerField(null=True, blank=True)

    # Target
    target = models.BooleanField(default=False)

    # ETL metadata
    etl_batch_id = models.CharField(max_length=50, blank=True, default='')

    class Meta:
        verbose_name = 'Fact: Patient Health'
        verbose_name_plural = 'Fact: Patient Health Records'

    def __str__(self):
        return f"Patient Fact {self.id} - Age: {self.age}, Target: {self.target}"


# ============================================================
# ETL LOG — Operational Metadata
# ============================================================

class ETLLog(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('RUNNING', 'Running'),
    ]

    batch_id = models.CharField(max_length=50, unique=True)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='RUNNING')

    records_extracted = models.IntegerField(default=0)
    records_validated = models.IntegerField(default=0)
    records_invalid = models.IntegerField(default=0)
    duplicates_detected = models.IntegerField(default=0)
    records_transformed = models.IntegerField(default=0)
    records_loaded = models.IntegerField(default=0)
    missing_values_handled = models.IntegerField(default=0)

    duration_seconds = models.FloatField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')
    data_quality_report = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'ETL Execution Log'
        verbose_name_plural = 'ETL Execution Logs'
        ordering = ['-started_at']

    def __str__(self):
        return f"ETL {self.batch_id} - {self.status} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"

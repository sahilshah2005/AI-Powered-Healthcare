from django.db import models

class DimGender(models.Model):
    gender_name = models.CharField(max_length=10) # Male, Female

    def __str__(self):
        return self.gender_name

class DimAgeGroup(models.Model):
    age_range = models.CharField(max_length=20) # '20-29', '30-39', etc.

    def __str__(self):
        return self.age_range

class DimChestPainType(models.Model):
    cp_name = models.CharField(max_length=50) # 'Typical Angina', 'Atypical Angina', etc.

    def __str__(self):
        return self.cp_name

class DimRestECG(models.Model):
    ecg_result = models.CharField(max_length=50) # 'Normal', 'ST-T wave abnormality', etc.

    def __str__(self):
        return self.ecg_result

class PatientFact(models.Model):
    # Foreign Keys to Dimensions
    gender = models.ForeignKey(DimGender, on_delete=models.CASCADE)
    age_group = models.ForeignKey(DimAgeGroup, on_delete=models.CASCADE)
    cp_type = models.ForeignKey(DimChestPainType, on_delete=models.CASCADE)
    rest_ecg = models.ForeignKey(DimRestECG, on_delete=models.CASCADE)
    
    # Continuous Facts
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
    target = models.BooleanField(default=False) # True if heart disease presence

    def __str__(self):
        return f"Patient Fact {self.id} - Target: {self.target}"

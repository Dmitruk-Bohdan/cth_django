# core/models.py
from django.db import models


class User(models.Model):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=128, db_column='password_hash')
    email = models.CharField(max_length=254, unique=True)
    role = models.SmallIntegerField()
    is_email_verified = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(blank=True, null=True)
    avatar_id = models.BigIntegerField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return f"{self.username} ({self.email})"


class Subject(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'subject'

    def __str__(self):
        return self.name


class Section(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, models.RESTRICT, db_column='subject_id')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'section'

    def __str__(self):
        return f"{self.name} ({self.subject.name})"


class Topic(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    section = models.ForeignKey(Section, models.RESTRICT, db_column='section_id')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'topic'

    def __str__(self):
        return self.name


class Problem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    topic = models.ForeignKey(Topic, models.RESTRICT, db_column='topic_id')
    author = models.ForeignKey(User, models.RESTRICT, db_column='author_id', related_name='authored_problems')
    is_deleted = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'problem'

    def __str__(self):
        return f"Problem #{self.id} (Topic: {self.topic.name})"


class ProblemVersion(models.Model):
    id = models.BigIntegerField(primary_key=True)
    problem = models.ForeignKey(Problem, models.RESTRICT, db_column='problem_id', related_name='versions')
    type = models.SmallIntegerField()  # 1=SingleChoice, 2=MultipleChoice, 3=OpenEnded
    difficulty = models.SmallIntegerField()  # 1-5
    statement = models.TextField()
    correct_answer = models.CharField(max_length=32, db_column='correct_answer')
    explanation = models.TextField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'problem_version'

    def __str__(self):
        return f"Version {self.id} of Problem {self.problem_id}"


class Test(models.Model):
    id = models.BigIntegerField(primary_key=True)
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, models.RESTRICT, db_column='subject_id')
    author = models.ForeignKey(User, models.RESTRICT, db_column='author_id', related_name='authored_tests')
    type = models.SmallIntegerField()
    is_traning = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    duration = models.IntegerField()
    attempts_count = models.IntegerField()
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test'

    def __str__(self):
        return self.title


class TestProblem(models.Model):
    id = models.BigIntegerField(primary_key=True)
    test = models.ForeignKey(Test, models.RESTRICT, db_column='test_id', related_name='test_problems')
    problem = models.ForeignKey(Problem, models.RESTRICT, db_column='problem_id', related_name='test_problems')
    code = models.CharField(max_length=3)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_problem'

    def __str__(self):
        return f"{self.test.title} - {self.code}"


class TestAttempt(models.Model):
    id = models.BigIntegerField(primary_key=True)
    test = models.ForeignKey(Test, models.RESTRICT, db_column='test_id')
    student = models.ForeignKey(User, models.RESTRICT, db_column='student_id', related_name='test_attempts')
    status = models.SmallIntegerField()  # 1=InProgress, 2=Completed, 3=Cancelled
    duration = models.IntegerField()
    raw_score = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    last_resumed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'test_attempt'

    def __str__(self):
        return f"Attempt {self.id}: {self.student.username} - {self.test.title}"


class UserAnswer(models.Model):
    id = models.BigIntegerField(primary_key=True)
    test_attempt = models.ForeignKey(TestAttempt, models.RESTRICT, db_column='test_attempt_id', related_name='user_answers')
    problem_version = models.ForeignKey(ProblemVersion, models.RESTRICT, db_column='problem_version_id')
    answer = models.CharField(max_length=32)
    is_correct = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_answer'

    def __str__(self):
        return f"Answer to {self.problem_version.problem_id}: {self.answer} ({self.is_correct})"


class Group(models.Model):
    id = models.BigIntegerField(primary_key=True)
    teacher = models.ForeignKey(User, models.CASCADE, db_column='teacher_id', related_name='groups')
    name = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, models.RESTRICT, db_column='subject_id')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '"group"'  # group is reserved word in SQL

    def __str__(self):
        return f"{self.name} (Teacher: {self.teacher.username})"


class TeacherStudent(models.Model):
    id = models.BigIntegerField(primary_key=True)
    teacher = models.ForeignKey(User, models.RESTRICT, db_column='teacher_id', related_name='students')
    student = models.ForeignKey(User, models.RESTRICT, db_column='student_id', related_name='teachers')
    status = models.SmallIntegerField()  # 1=Active, 2=Blocked, 3=Pending
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'teacher_student'

    def __str__(self):
        return f"{self.teacher.username} -> {self.student.username}"


class StudentGroupStudent(models.Model):
    group = models.ForeignKey(Group, models.CASCADE, db_column='group_id')
    student = models.ForeignKey(User, models.CASCADE, db_column='student_id')

    class Meta:
        managed = False
        db_table = 'student_group_student'
        unique_together = (('group', 'student'),)
    
    def __str__(self):
        return f"{self.student.username} in {self.group.name}"


class GroupAssignment(models.Model):
    group = models.ForeignKey(Group, models.SET_NULL, db_column='group_id', blank=True, null=True, related_name='group_assignments')
    teacher = models.ForeignKey(User, models.RESTRICT, db_column='teacher_id', related_name='group_assignments')
    test = models.ForeignKey(Test, models.RESTRICT, db_column='test_id')
    expired_at = models.DateTimeField()
    default_attempts_allowed = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'group_assignment'

    def __str__(self):
        return f"Group {self.group_id} - {self.test.title}"


class StudentAssignment(models.Model):
    id = models.BigIntegerField(primary_key=True)
    student = models.ForeignKey(User, models.RESTRICT, db_column='student_id', related_name='student_assignments')
    teacher = models.ForeignKey(User, models.RESTRICT, db_column='teacher_id', related_name='teacher_assignments')
    group_assignment = models.ForeignKey(GroupAssignment, models.RESTRICT, db_column='group_assignment_id', blank=True, null=True)
    test = models.ForeignKey(Test, models.RESTRICT, db_column='test_id')
    expired_at = models.DateTimeField()
    attempts_left = models.SmallIntegerField(blank=True, null=True)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'student_assignment'

    def __str__(self):
        return f"{self.student.username} - {self.test.title} (expires: {self.expired_at})"


class Notification(models.Model):
    id = models.BigIntegerField(primary_key=True)
    recipient = models.ForeignKey(User, models.CASCADE, db_column='recipient_id', related_name='notifications')
    priority_level = models.SmallIntegerField()  # 1=Low, 2=Medium, 3=High
    payload = models.TextField()
    is_seen = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'notification'

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.payload[:50]}..."


class InvitationCode(models.Model):
    id = models.BigIntegerField(primary_key=True)
    teacher = models.ForeignKey(User, models.CASCADE, db_column='teacher_id')
    code = models.CharField(max_length=36)
    uses_left = models.SmallIntegerField(blank=True, null=True)
    expired_at = models.DateTimeField(blank=True, null=True)
    is_revoked = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'invitation_code'

    def __str__(self):
        return f"Code {self.code} for teacher {self.teacher.username}"


class BindingRequest(models.Model):
    id = models.BigIntegerField(primary_key=True)
    code = models.ForeignKey(InvitationCode, models.RESTRICT, db_column='code_id')
    student = models.ForeignKey(User, models.RESTRICT, db_column='student_id')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'binding_request'

    def __str__(self):
        return f"Binding request from {self.student.username} to code {self.code.code}"


class UserSession(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User, models.RESTRICT, db_column='user_id', related_name='sessions')
    jti = models.UUIDField()
    client_type = models.SmallIntegerField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    device_info = models.JSONField(blank=True, null=True)
    last_activity_at = models.DateTimeField()
    created_at = models.DateTimeField()
    last_update_at = models.DateTimeField()
    revoked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_session'

    def __str__(self):
        return f"Session {self.user.username} - {self.client_type}"


class RefreshToken(models.Model):
    id = models.BigIntegerField(primary_key=True)
    session = models.OneToOneField(UserSession, models.RESTRICT, db_column='session_id', related_name='refresh_token')
    token_hash = models.CharField(max_length=128)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField()
    revoked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'refresh_token'

    def __str__(self):
        return f"Refresh token for session {self.session_id}"


class Image(models.Model):
    id = models.BigIntegerField(primary_key=True)
    object_key = models.TextField()
    bucket = models.TextField()
    owner = models.ForeignKey(User, models.RESTRICT, db_column='owner_id', related_name='images')
    content_type = models.TextField()
    size = models.BigIntegerField()
    created_at = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'image'

    def __str__(self):
        return f"Image {self.id} - {self.object_key}"


class EmailVerificationToken(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, db_column='user_id')
    token_hash = models.CharField(max_length=128)
    attempts_left = models.SmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'email_verification_code'

    def __str__(self):
        return f"Email verification for {self.user.email}"


class PasswordResetToken(models.Model):
    id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, db_column='user_id')
    token_hash = models.CharField(max_length=128)
    attempts_left = models.SmallIntegerField(default=5)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'password_reset_token'

    def __str__(self):
        return f"Password reset for {self.user.email}"
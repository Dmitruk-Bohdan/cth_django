# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User, Subject, Section, Topic, Problem, ProblemVersion,
    Test, TestProblem, TestAttempt, UserAnswer,
    Group, TeacherStudent, StudentGroupStudent,
    GroupAssignment, StudentAssignment, Notification,
    InvitationCode, BindingRequest, UserSession, RefreshToken,
    Image, EmailVerificationToken, PasswordResetToken
)


# ============================================================
# ПОЛЬЗОВАТЕЛИ И АВТОРИЗАЦИЯ
# ============================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role_display', 'is_email_verified', 'is_deleted')
    list_filter = ('role', 'is_email_verified', 'is_deleted')
    search_fields = ('username', 'email')
    readonly_fields = ('created_at', 'last_update_at', 'password_hash')
    actions = ['soft_delete', 'restore']
    
    fieldsets = (
        ('Основная информация', {'fields': ('username', 'email', 'role')}),
        ('Статус', {'fields': ('is_email_verified', 'is_deleted')}),
        ('Даты', {'fields': ('created_at', 'last_update_at', 'last_login_at')}),
        ('Безопасность', {'fields': ('password_hash',)}),
    )
    
    def role_display(self, obj):
        roles = {1: '👨‍🎓 Ученик', 2: '👨‍🏫 Учитель', 3: '👑 Администратор'}
        return roles.get(obj.role, '❓ Неизвестно')
    role_display.short_description = 'Роль'
    
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = 'Мягкое удаление (is_deleted=True)'
    
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = 'Восстановить (is_deleted=False)'


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'client_type_display', 'ip_address', 'last_activity_at', 'is_active')
    list_filter = ('client_type',)
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('created_at', 'last_update_at')
    
    def client_type_display(self, obj):
        types = {1: '🌐 Web', 2: '📱 Mobile', 3: '🖥️ Desktop'}
        return types.get(obj.client_type, '❓')
    client_type_display.short_description = 'Тип клиента'
    
    def is_active(self, obj):
        return obj.revoked_at is None
    is_active.boolean = True
    is_active.short_description = 'Активна'


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'expires_at', 'is_revoked')
    list_filter = ('expires_at',)
    search_fields = ('session__user__username',)
    
    def is_revoked(self, obj):
        return obj.revoked_at is not None
    is_revoked.boolean = True
    is_revoked.short_description = 'Отозван'


@admin.register(InvitationCode)
class InvitationCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'teacher', 'uses_left', 'expired_at', 'is_revoked')
    list_filter = ('is_revoked',)
    search_fields = ('code', 'teacher__username')
    readonly_fields = ('created_at', 'last_update_at')


@admin.register(BindingRequest)
class BindingRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'code', 'is_accepted', 'created_at')
    list_filter = ('is_accepted',)
    search_fields = ('student__username', 'code__code')
    readonly_fields = ('created_at', 'last_update_at')


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'attempts_left', 'expires_at', 'verified_at')
    list_filter = ('verified_at',)
    search_fields = ('user__email',)
    readonly_fields = ('token_hash',)


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'attempts_left', 'expires_at', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('user__email',)
    readonly_fields = ('token_hash',)


# ============================================================
# ПРЕДМЕТЫ, РАЗДЕЛЫ, ТЕМЫ
# ============================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_deleted', 'created_at')
    list_filter = ('is_deleted',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_update_at')


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'is_deleted')
    list_filter = ('subject', 'is_deleted')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_update_at')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'section', 'is_deleted')
    list_filter = ('section__subject', 'section', 'is_deleted')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'last_update_at')


# ============================================================
# ЗАДАНИЯ (PROBLEMS)
# ============================================================

class ProblemVersionInline(admin.TabularInline):
    model = ProblemVersion
    extra = 0
    fields = ('type', 'difficulty', 'statement_preview', 'is_active')
    readonly_fields = ('statement_preview',)
    
    def statement_preview(self, obj):
        if obj.statement:
            try:
                import json
                data = json.loads(obj.statement)
                return data.get('statement', '')[:100] + '...'
            except:
                return obj.statement[:100] + '...'
        return '-'
    statement_preview.short_description = 'Текст задания'


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'author', 'is_published', 'is_public', 'is_deleted')
    list_filter = ('is_published', 'is_public', 'is_deleted', 'topic__section__subject')
    search_fields = ('id', 'author__username')
    inlines = [ProblemVersionInline]
    actions = ['publish', 'unpublish', 'make_public', 'make_private']
    
    def publish(self, request, queryset):
        queryset.update(is_published=True)
    publish.short_description = 'Опубликовать'
    
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
    unpublish.short_description = 'Снять с публикации'
    
    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = 'Сделать приватными'


@admin.register(ProblemVersion)
class ProblemVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'problem', 'type_display', 'difficulty_display', 'is_active', 'created_at')
    list_filter = ('type', 'difficulty', 'is_active')
    search_fields = ('problem__id',)
    readonly_fields = ('created_at',)
    
    def type_display(self, obj):
        types = {1: '🔘 SingleChoice', 2: '☑️ MultipleChoice', 3: '✏️ OpenEnded'}
        return types.get(obj.type, '❓')
    type_display.short_description = 'Тип'
    
    def difficulty_display(self, obj):
        difficulties = {1: '⭐', 2: '⭐⭐', 3: '⭐⭐⭐', 4: '⭐⭐⭐⭐', 5: '⭐⭐⭐⭐⭐'}
        return difficulties.get(obj.difficulty, '❓')
    difficulty_display.short_description = 'Сложность'


# ============================================================
# ТЕСТЫ
# ============================================================

class TestProblemInline(admin.TabularInline):
    model = TestProblem
    extra = 1
    fields = ('problem', 'code')
    search_fields = ('problem__id',)
    ordering = ('code',)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'subject', 'is_published', 'is_public', 'is_traning', 'type')
    list_filter = ('subject', 'is_published', 'is_public', 'is_traning', 'type')
    search_fields = ('title', 'author__username')
    readonly_fields = ('created_at', 'last_update_at')
    inlines = [TestProblemInline]
    actions = ['publish', 'unpublish', 'make_public', 'make_private']
    
    def publish(self, request, queryset):
        queryset.update(is_published=True)
    publish.short_description = 'Опубликовать'
    
    def unpublish(self, request, queryset):
        queryset.update(is_published=False)
    unpublish.short_description = 'Снять с публикации'
    
    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = 'Сделать публичными'
    
    def make_private(self, request, queryset):
        queryset.update(is_public=False)
    make_private.short_description = 'Сделать приватными'


@admin.register(TestProblem)
class TestProblemAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'problem', 'code')
    list_filter = ('test__author', 'test__subject')
    search_fields = ('test__title', 'problem__id')
    ordering = ('test', 'code')


# ============================================================
# ПОПЫТКИ И ОТВЕТЫ
# ============================================================

class UserAnswerInline(admin.TabularInline):
    model = UserAnswer
    extra = 0
    fields = ('problem_version', 'answer', 'is_correct')
    readonly_fields = ('created_at',)


@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'student', 'status_display', 'raw_score', 'duration', 'created_at')
    list_filter = ('status', 'test__subject')
    search_fields = ('student__username', 'test__title')
    readonly_fields = ('created_at', 'last_resumed_at')
    inlines = [UserAnswerInline]
    
    def status_display(self, obj):
        statuses = {1: '🟡 В процессе', 2: '✅ Завершён', 3: '❌ Отменён'}
        return statuses.get(obj.status, '❓')
    status_display.short_description = 'Статус'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_attempt', 'problem_version', 'answer', 'is_correct_badge')
    list_filter = ('is_correct',)
    search_fields = ('test_attempt__student__username',)
    readonly_fields = ('created_at',)
    
    def is_correct_badge(self, obj):
        if obj.is_correct:
            return True  # ✅ вместо '✅ Верно'
        return False     # ❌ вместо '❌ Неверно'
    is_correct_badge.boolean = True  # ← эта строка важна
    is_correct_badge.short_description = 'Правильно'


# ============================================================
# ГРУППЫ И СВЯЗИ
# ============================================================

class StudentGroupStudentInline(admin.TabularInline):
    model = StudentGroupStudent
    extra = 1
    fields = ('student',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'subject', 'is_deleted')
    list_filter = ('subject', 'is_deleted')
    search_fields = ('name', 'teacher__username')
    readonly_fields = ('created_at', 'last_update_at')
    inlines = [StudentGroupStudentInline]
    actions = ['soft_delete', 'restore']
    
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = 'Мягкое удаление'
    
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = 'Восстановить'


@admin.register(TeacherStudent)
class TeacherStudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'teacher', 'student', 'status_display', 'is_deleted')
    list_filter = ('status', 'is_deleted')
    search_fields = ('teacher__username', 'student__username')
    readonly_fields = ('created_at', 'last_update_at')
    
    def status_display(self, obj):
        statuses = {1: '🟢 Активен', 2: '🔴 Заблокирован', 3: '🟡 Ожидание'}
        return statuses.get(obj.status, '❓')
    status_display.short_description = 'Статус'


# @admin.register(StudentGroupStudent)
# class StudentGroupStudentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'group', 'student')
#     list_filter = ('group__subject',)
#     search_fields = ('group__name', 'student__username')


# ============================================================
# НАЗНАЧЕНИЯ
# ============================================================

class StudentAssignmentInline(admin.TabularInline):
    model = StudentAssignment
    extra = 0
    fields = ('student', 'test', 'expired_at', 'attempts_left')
    readonly_fields = ('created_at', 'last_update_at')


@admin.register(GroupAssignment)
class GroupAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'teacher', 'test', 'expired_at', 'default_attempts_allowed')
    list_filter = ('teacher', 'is_deleted')
    search_fields = ('group__name', 'test__title')
    readonly_fields = ('created_at', 'last_update_at')
    inlines = [StudentAssignmentInline]
    actions = ['soft_delete', 'restore']
    
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = 'Мягкое удаление'
    
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = 'Восстановить'


@admin.register(StudentAssignment)
class StudentAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'teacher', 'test', 'expired_at', 'attempts_left', 'is_deleted')
    list_filter = ('teacher', 'is_deleted')
    search_fields = ('student__username', 'test__title')
    readonly_fields = ('created_at', 'last_update_at')
    actions = ['soft_delete', 'restore']
    
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)
    soft_delete.short_description = 'Мягкое удаление'
    
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)
    restore.short_description = 'Восстановить'


# ============================================================
# УВЕДОМЛЕНИЯ
# ============================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'priority_display', 'is_seen', 'created_at')
    list_filter = ('priority_level', 'is_seen', 'is_deleted')
    search_fields = ('recipient__username', 'payload')
    readonly_fields = ('created_at',)
    actions = ['mark_as_seen', 'mark_as_unseen']
    
    def priority_display(self, obj):
        levels = {1: '🟢 Низкий', 2: '🟡 Средний', 3: '🔴 Высокий'}
        return levels.get(obj.priority_level, '❓')
    priority_display.short_description = 'Приоритет'
    
    def mark_as_seen(self, request, queryset):
        queryset.update(is_seen=True)
    mark_as_seen.short_description = 'Отметить как прочитанные'
    
    def mark_as_unseen(self, request, queryset):
        queryset.update(is_seen=False)
    mark_as_unseen.short_description = 'Отметить как непрочитанные'


# ============================================================
# ИЗОБРАЖЕНИЯ
# ============================================================

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'content_type', 'size_kb', 'created_at', 'is_deleted')
    list_filter = ('content_type', 'is_deleted')
    search_fields = ('owner__username', 'object_key')
    readonly_fields = ('created_at',)
    
    def size_kb(self, obj):
        return f"{obj.size // 1024} KB"
    size_kb.short_description = 'Размер'
"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CourseFormModal, useCourseCenterId } from "@/components/CourseFormModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  EmptyState,
  Input,
  PageHeader,
  PageSection,
  CardSkeleton,
} from "@/components/ui";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";
import { cn } from "@/lib/cn";

type Course = {
  id: string;
  name: string;
  subject_id: string;
  subject_name_uz: string | null;
  description: string | null;
  price: number | null;
  duration_weeks: number | null;
  is_active: boolean;
  lesson_count: number;
};

type Lesson = {
  id: string;
  title: string;
  scheduled_at: string | null;
  duration_minutes: number;
  room: string | null;
};

export default function CoursesPage() {
  const t = useTranslations("courses");
  const { can } = usePermissions();
  const centerId = useCourseCenterId();
  const [courses, setCourses] = useState<Course[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);
  const [lessonTitle, setLessonTitle] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editCourse, setEditCourse] = useState<Course | null>(null);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);
  const [editLessonTitle, setEditLessonTitle] = useState("");

  const loadCourses = useCallback(() => {
    setLoading(true);
    apiFetch<Course[]>("/courses")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setCourses(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    loadCourses();
    apiFetch<{ id: string; name_uz: string }[]>("/subjects").then((res) => {
      if (res.success && Array.isArray(res.data)) setSubjects(res.data);
    });
  }, [loadCourses]);

  const loadLessons = useCallback((courseId: string) => {
    apiFetch<Lesson[]>(`/courses/${courseId}/lessons`).then((res) => {
      if (res.success && Array.isArray(res.data)) setLessons(res.data);
    });
  }, []);

  useEffect(() => {
    if (!selectedCourse) {
      setLessons([]);
      return;
    }
    loadLessons(selectedCourse.id);
  }, [selectedCourse, loadLessons]);

  const addLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCourse) return;
    await apiFetch(`/courses/${selectedCourse.id}/lessons`, {
      method: "POST",
      body: JSON.stringify({ title: lessonTitle }),
    });
    setLessonTitle("");
    loadLessons(selectedCourse.id);
    loadCourses();
  };

  const saveLessonEdit = async () => {
    if (!selectedCourse || !editingLesson) return;
    await apiFetch(`/courses/${selectedCourse.id}/lessons/${editingLesson.id}`, {
      method: "PATCH",
      body: JSON.stringify({ title: editLessonTitle }),
    });
    setEditingLesson(null);
    loadLessons(selectedCourse.id);
  };

  const deleteLesson = async (lesson: Lesson) => {
    if (!selectedCourse || !window.confirm(t("deleteLessonConfirm", { title: lesson.title }))) return;
    await apiFetch(`/courses/${selectedCourse.id}/lessons/${lesson.id}`, { method: "DELETE" });
    loadLessons(selectedCourse.id);
    loadCourses();
  };

  const deleteCourse = async (course: Course) => {
    if (!window.confirm(t("deleteConfirm", { name: course.name }))) return;
    await apiFetch(`/courses/${course.id}`, { method: "DELETE" });
    if (selectedCourse?.id === course.id) setSelectedCourse(null);
    loadCourses();
  };

  return (
    <PageSection>
      <PageHeader
        title={t("title")}
        actions={
          <PermissionGate permission="courses.create">
            {centerId && (
              <Button
                onClick={() => {
                  setEditCourse(null);
                  setShowForm(true);
                }}
              >
                {t("add")}
              </Button>
            )}
          </PermissionGate>
        }
      />

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : courses.length === 0 ? (
        <EmptyState title={t("empty")} />
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {courses.map((course) => (
            <Card
              key={course.id}
              hover
              className={cn(selectedCourse?.id === course.id && "ring-2 ring-naqsh-accent")}
            >
              <CardBody>
                <button type="button" onClick={() => setSelectedCourse(course)} className="w-full text-left">
                  <CardTitle>{course.name}</CardTitle>
                  <CardDescription>{course.subject_name_uz}</CardDescription>
                  <p className="text-small text-muted-foreground mt-2">
                    {t("lessons")}: {course.lesson_count}
                    {course.duration_weeks ? ` · ${course.duration_weeks} ${t("weeks")}` : ""}
                    {course.price != null ? ` · ${course.price.toLocaleString()} UZS` : ""}
                  </p>
                  {!course.is_active && (
                    <Badge variant="default" className="mt-2">
                      {t("inactive")}
                    </Badge>
                  )}
                </button>
                {(can("courses.update") || can("courses.delete")) && (
                  <div className="flex gap-2 mt-3 pt-3 border-t border-border">
                    {can("courses.update") && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setEditCourse(course);
                          setShowForm(true);
                        }}
                      >
                        {t("edit")}
                      </Button>
                    )}
                    {can("courses.delete") && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-danger hover:text-danger"
                        onClick={() => deleteCourse(course)}
                      >
                        {t("delete")}
                      </Button>
                    )}
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {selectedCourse && (
        <Card>
          <CardBody className="space-y-3">
            <CardTitle>{t("lessonSchedule")}</CardTitle>
            <PermissionGate permission="courses.update">
              <form onSubmit={addLesson} className="flex gap-2">
                <Input
                  className="flex-1"
                  placeholder={t("lessonTitle")}
                  value={lessonTitle}
                  onChange={(e) => setLessonTitle(e.target.value)}
                  required
                />
                <Button type="submit">{t("addLesson")}</Button>
              </form>
            </PermissionGate>
            <ul className="space-y-2">
              {lessons.map((lesson) => (
                <li
                  key={lesson.id}
                  className="text-small border border-border rounded-lg px-3 py-2 flex justify-between gap-2"
                >
                  {editingLesson?.id === lesson.id ? (
                    <div className="flex flex-1 gap-2">
                      <Input
                        className="flex-1"
                        value={editLessonTitle}
                        onChange={(e) => setEditLessonTitle(e.target.value)}
                      />
                      <Button type="button" variant="ghost" size="sm" onClick={saveLessonEdit}>
                        {t("save")}
                      </Button>
                      <Button type="button" variant="ghost" size="sm" onClick={() => setEditingLesson(null)}>
                        {t("cancel")}
                      </Button>
                    </div>
                  ) : (
                    <>
                      <div>
                        <span className="font-medium">{lesson.title}</span>
                        {lesson.scheduled_at && (
                          <span className="text-muted-foreground ml-2">
                            {new Date(lesson.scheduled_at).toLocaleString()}
                          </span>
                        )}
                        {lesson.room && <span className="text-muted-foreground ml-2">· {lesson.room}</span>}
                      </div>
                      {can("courses.update") && (
                        <div className="flex gap-2 shrink-0">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setEditingLesson(lesson);
                              setEditLessonTitle(lesson.title);
                            }}
                          >
                            {t("edit")}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-danger hover:text-danger"
                            onClick={() => deleteLesson(lesson)}
                          >
                            {t("delete")}
                          </Button>
                        </div>
                      )}
                    </>
                  )}
                </li>
              ))}
              {lessons.length === 0 && (
                <li className="text-muted-foreground text-small">{t("noLessons")}</li>
              )}
            </ul>
          </CardBody>
        </Card>
      )}

      {showForm && centerId && (
        <CourseFormModal
          centerId={centerId}
          course={editCourse}
          subjects={subjects}
          onClose={() => setShowForm(false)}
          onSaved={loadCourses}
        />
      )}
    </PageSection>
  );
}

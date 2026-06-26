"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { CourseFormModal, useCourseCenterId } from "@/components/CourseFormModal";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch } from "@/lib/api";
import { usePermissions } from "@/hooks/usePermissions";

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
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
        <PermissionGate permission="courses.create">
          {centerId && (
            <button
              type="button"
              onClick={() => {
                setEditCourse(null);
                setShowForm(true);
              }}
              className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm font-medium"
            >
              {t("add")}
            </button>
          )}
        </PermissionGate>
      </div>

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {courses.map((course) => (
            <div
              key={course.id}
              className={`bg-white rounded-xl border p-4 shadow-sm ${
                selectedCourse?.id === course.id ? "ring-2 ring-naqsh-accent" : ""
              }`}
            >
              <button type="button" onClick={() => setSelectedCourse(course)} className="w-full text-left">
                <h3 className="font-semibold text-naqsh-primary">{course.name}</h3>
                <p className="text-sm text-gray-600">{course.subject_name_uz}</p>
                <p className="text-sm text-gray-500">
                  {t("lessons")}: {course.lesson_count}
                  {course.duration_weeks ? ` · ${course.duration_weeks} ${t("weeks")}` : ""}
                  {course.price != null ? ` · ${course.price.toLocaleString()} UZS` : ""}
                </p>
                {!course.is_active && (
                  <span className="text-xs text-gray-400">{t("inactive")}</span>
                )}
              </button>
              {(can("courses.update") || can("courses.delete")) && (
                <div className="flex gap-3 mt-2 pt-2 border-t">
                  {can("courses.update") && (
                    <button
                      type="button"
                      className="text-naqsh-accent text-sm hover:underline"
                      onClick={() => {
                        setEditCourse(course);
                        setShowForm(true);
                      }}
                    >
                      {t("edit")}
                    </button>
                  )}
                  {can("courses.delete") && (
                    <button
                      type="button"
                      className="text-red-600 text-sm hover:underline"
                      onClick={() => deleteCourse(course)}
                    >
                      {t("delete")}
                    </button>
                  )}
                </div>
              )}
            </div>
          ))}
          {courses.length === 0 && <p className="text-gray-400">{t("empty")}</p>}
        </div>
      )}

      {selectedCourse && (
        <div className="bg-white rounded-xl border p-4 space-y-3">
          <h3 className="font-semibold text-naqsh-primary">{t("lessonSchedule")}</h3>
          <PermissionGate permission="courses.update">
            <form onSubmit={addLesson} className="flex gap-2">
              <input
                className="flex-1 border rounded-lg px-3 py-2"
                placeholder={t("lessonTitle")}
                value={lessonTitle}
                onChange={(e) => setLessonTitle(e.target.value)}
                required
              />
              <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg">
                {t("addLesson")}
              </button>
            </form>
          </PermissionGate>
          <ul className="space-y-2">
            {lessons.map((lesson) => (
              <li key={lesson.id} className="text-sm border rounded-lg px-3 py-2 flex justify-between gap-2">
                {editingLesson?.id === lesson.id ? (
                  <div className="flex flex-1 gap-2">
                    <input
                      className="flex-1 border rounded px-2 py-1"
                      value={editLessonTitle}
                      onChange={(e) => setEditLessonTitle(e.target.value)}
                    />
                    <button type="button" onClick={saveLessonEdit} className="text-naqsh-accent text-xs">
                      {t("save")}
                    </button>
                    <button
                      type="button"
                      onClick={() => setEditingLesson(null)}
                      className="text-gray-500 text-xs"
                    >
                      {t("cancel")}
                    </button>
                  </div>
                ) : (
                  <>
                    <div>
                      <span className="font-medium">{lesson.title}</span>
                      {lesson.scheduled_at && (
                        <span className="text-gray-500 ml-2">
                          {new Date(lesson.scheduled_at).toLocaleString()}
                        </span>
                      )}
                      {lesson.room && <span className="text-gray-500 ml-2">· {lesson.room}</span>}
                    </div>
                    {can("courses.update") && (
                      <div className="flex gap-2 shrink-0">
                        <button
                          type="button"
                          className="text-naqsh-accent text-xs hover:underline"
                          onClick={() => {
                            setEditingLesson(lesson);
                            setEditLessonTitle(lesson.title);
                          }}
                        >
                          {t("edit")}
                        </button>
                        <button
                          type="button"
                          className="text-red-600 text-xs hover:underline"
                          onClick={() => deleteLesson(lesson)}
                        >
                          {t("delete")}
                        </button>
                      </div>
                    )}
                  </>
                )}
              </li>
            ))}
            {lessons.length === 0 && <li className="text-gray-400 text-sm">{t("noLessons")}</li>}
          </ul>
        </div>
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
    </div>
  );
}

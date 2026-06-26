"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch } from "@/lib/api";

type Course = {
  id: string;
  name: string;
  subject_name_uz: string | null;
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
  const [courses, setCourses] = useState<Course[]>([]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);
  const [lessonTitle, setLessonTitle] = useState("");

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
      if (res.success && Array.isArray(res.data)) {
        setSubjects(res.data);
        if (res.data[0]) setSubjectId(res.data[0].id);
      }
    });
  }, [loadCourses]);

  useEffect(() => {
    if (!selectedCourse) {
      setLessons([]);
      return;
    }
    apiFetch<Lesson[]>(`/courses/${selectedCourse}/lessons`).then((res) => {
      if (res.success && Array.isArray(res.data)) setLessons(res.data);
    });
  }, [selectedCourse]);

  const createCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/courses", {
      method: "POST",
      body: JSON.stringify({ name, subject_id: subjectId }),
    });
    setName("");
    loadCourses();
  };

  const addLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCourse) return;
    await apiFetch(`/courses/${selectedCourse}/lessons`, {
      method: "POST",
      body: JSON.stringify({ title: lessonTitle }),
    });
    setLessonTitle("");
    const res = await apiFetch<Lesson[]>(`/courses/${selectedCourse}/lessons`);
    if (res.success && Array.isArray(res.data)) setLessons(res.data);
    loadCourses();
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
      <PermissionGate permission="courses.create">
        <form onSubmit={createCourse} className="bg-white p-4 rounded-xl border space-y-3">
          <input
            className="w-full border rounded-lg px-3 py-2"
            placeholder={t("name")}
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <select className="w-full border rounded-lg px-3 py-2" value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
            <option value="">{t("selectSubject")}</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.name_uz}</option>
            ))}
          </select>
          <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg">{t("add")}</button>
        </form>
      </PermissionGate>

      {loading ? (
        <p className="text-gray-400">{t("loading")}</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {courses.map((course) => (
            <button
              key={course.id}
              type="button"
              onClick={() => setSelectedCourse(course.id)}
              className={`text-left bg-white rounded-xl border p-4 shadow-sm ${
                selectedCourse === course.id ? "ring-2 ring-naqsh-accent" : ""
              }`}
            >
              <h3 className="font-semibold text-naqsh-primary">{course.name}</h3>
              <p className="text-sm text-gray-600">{course.subject_name_uz}</p>
              <p className="text-sm text-gray-500">
                {t("lessons")}: {course.lesson_count}
                {course.duration_weeks ? ` · ${course.duration_weeks} ${t("weeks")}` : ""}
              </p>
            </button>
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
              <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg">{t("addLesson")}</button>
            </form>
          </PermissionGate>
          <ul className="space-y-2">
            {lessons.map((lesson) => (
              <li key={lesson.id} className="text-sm border rounded-lg px-3 py-2">
                <span className="font-medium">{lesson.title}</span>
                {lesson.scheduled_at && (
                  <span className="text-gray-500 ml-2">{new Date(lesson.scheduled_at).toLocaleString()}</span>
                )}
                {lesson.room && <span className="text-gray-500 ml-2">· {lesson.room}</span>}
              </li>
            ))}
            {lessons.length === 0 && <li className="text-gray-400 text-sm">{t("noLessons")}</li>}
          </ul>
        </div>
      )}
    </div>
  );
}

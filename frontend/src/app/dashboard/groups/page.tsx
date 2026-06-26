"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { EnrollStudentModal } from "@/components/EnrollStudentModal";
import { AssignTeacherModal } from "@/components/AssignTeacherModal";
import { PermissionGate } from "@/components/PermissionGate";
import { apiFetch, getMe, listCenters } from "@/lib/api";

type Group = {
  id: string;
  name: string;
  subject_name_uz: string | null;
  teacher_id: string | null;
  teacher_name: string | null;
  room: string | null;
  enrollment_count: number;
  is_active: boolean;
};

export default function GroupsPage() {
  const t = useTranslations("groups");
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [centerId, setCenterId] = useState("");
  const [subjects, setSubjects] = useState<{ id: string; name_uz: string }[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [room, setRoom] = useState("");
  const [enrollGroup, setEnrollGroup] = useState<Group | null>(null);
  const [assignGroup, setAssignGroup] = useState<Group | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    apiFetch<Group[]>("/groups")
      .then((res) => {
        if (res.success && Array.isArray(res.data)) setGroups(res.data);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
    apiFetch<{ id: string; name_uz: string }[]>("/subjects").then((res) => {
      if (res.success && Array.isArray(res.data)) setSubjects(res.data);
    });
    getMe().then(async (res) => {
      if (res.data?.center_id) setCenterId(res.data.center_id as string);
      else {
        const centers = await listCenters();
        if (centers.success && Array.isArray(centers.data) && centers.data[0]) {
          setCenterId((centers.data[0] as { id: string }).id);
        }
      }
    });
  }, [load]);

  const createGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    await apiFetch("/groups", {
      method: "POST",
      body: JSON.stringify({ center_id: centerId, subject_id: subjectId, name, room: room || null }),
    });
    setShowForm(false);
    setName("");
    setRoom("");
    load();
  };

  return (
    <>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-naqsh-primary">{t("title")}</h2>
          <PermissionGate permission="groups.create">
            <button
              type="button"
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-naqsh-primary text-white rounded-lg text-sm"
            >
              {t("add")}
            </button>
          </PermissionGate>
        </div>
        {showForm && (
          <form onSubmit={createGroup} className="bg-white p-4 rounded-xl border space-y-3">
            <input className="w-full border rounded-lg px-3 py-2" placeholder={t("name")} value={name} onChange={(e) => setName(e.target.value)} required />
            <select className="w-full border rounded-lg px-3 py-2" value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
              <option value="">{t("selectSubject")}</option>
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>{s.name_uz}</option>
              ))}
            </select>
            <input className="w-full border rounded-lg px-3 py-2" placeholder={t("room")} value={room} onChange={(e) => setRoom(e.target.value)} />
            <div className="flex gap-2">
              <button type="submit" className="px-4 py-2 bg-naqsh-primary text-white rounded-lg">{t("save")}</button>
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 border rounded-lg">{t("cancel")}</button>
            </div>
          </form>
        )}
        {loading ? (
          <p className="text-gray-400">{t("loading")}</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {groups.map((g) => (
              <div key={g.id} className="bg-white rounded-xl border p-4 shadow-sm">
                <h3 className="font-semibold text-naqsh-primary">{g.name}</h3>
                <p className="text-sm text-gray-600">{g.subject_name_uz} · {g.teacher_name || t("noTeacher")}</p>
                <p className="text-sm text-gray-500">{t("room")}: {g.room || "—"} · {t("students")}: {g.enrollment_count}</p>
                <div className="mt-3 flex flex-wrap gap-3">
                  <PermissionGate permission="groups.update">
                    <button
                      type="button"
                      onClick={() => setAssignGroup(g)}
                      className="text-sm text-naqsh-primary hover:underline"
                    >
                      {g.teacher_name ? t("changeTeacher") : t("assignTeacher")}
                    </button>
                  </PermissionGate>
                  <PermissionGate permission="groups.enroll">
                    <button
                      type="button"
                      onClick={() => setEnrollGroup(g)}
                      className="text-sm text-naqsh-accent hover:underline"
                    >
                      {t("manageStudents")}
                    </button>
                  </PermissionGate>
                </div>
              </div>
            ))}
            {groups.length === 0 && <p className="text-gray-400">{t("empty")}</p>}
          </div>
        )}
      </div>
      {enrollGroup && (
        <EnrollStudentModal
          groupId={enrollGroup.id}
          groupName={enrollGroup.name}
          onClose={() => setEnrollGroup(null)}
          onChanged={load}
        />
      )}
      {assignGroup && (
        <AssignTeacherModal
          groupId={assignGroup.id}
          groupName={assignGroup.name}
          currentTeacherName={assignGroup.teacher_name}
          onClose={() => setAssignGroup(null)}
          onAssigned={load}
        />
      )}
    </>
  );
}

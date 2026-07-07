"use client";

import { useCallback, useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { EnrollStudentModal } from "@/components/EnrollStudentModal";
import { AssignTeacherModal } from "@/components/AssignTeacherModal";
import { PermissionGate } from "@/components/PermissionGate";
import {
  Button,
  Card,
  CardBody,
  CardDescription,
  CardTitle,
  EmptyState,
  FormActions,
  Input,
  PageHeader,
  PageSection,
  Select,
  CardSkeleton,
} from "@/components/ui";
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
      <PageSection>
        <PageHeader
          title={t("title")}
          actions={
            <PermissionGate permission="groups.create">
              <Button onClick={() => setShowForm(true)}>{t("add")}</Button>
            </PermissionGate>
          }
        />

        {showForm && (
          <Card>
            <CardBody>
              <form onSubmit={createGroup} className="space-y-3">
                <Input placeholder={t("name")} value={name} onChange={(e) => setName(e.target.value)} required />
                <Select value={subjectId} onChange={(e) => setSubjectId(e.target.value)} required>
                  <option value="">{t("selectSubject")}</option>
                  {subjects.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name_uz}
                    </option>
                  ))}
                </Select>
                <Input placeholder={t("room")} value={room} onChange={(e) => setRoom(e.target.value)} />
                <FormActions>
                  <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                    {t("cancel")}
                  </Button>
                  <Button type="submit">{t("save")}</Button>
                </FormActions>
              </form>
            </CardBody>
          </Card>
        )}

        {loading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        ) : groups.length === 0 ? (
          <EmptyState title={t("empty")} />
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {groups.map((g) => (
              <Card key={g.id} hover>
                <CardBody>
                  <CardTitle>{g.name}</CardTitle>
                  <CardDescription>
                    {g.subject_name_uz} · {g.teacher_name || t("noTeacher")}
                  </CardDescription>
                  <p className="text-small text-muted-foreground mt-2">
                    {t("room")}: {g.room || "—"} · {t("students")}: {g.enrollment_count}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <PermissionGate permission="groups.update">
                      <Button variant="ghost" size="sm" onClick={() => setAssignGroup(g)}>
                        {g.teacher_name ? t("changeTeacher") : t("assignTeacher")}
                      </Button>
                    </PermissionGate>
                    <PermissionGate permission="groups.enroll">
                      <Button variant="ghost" size="sm" onClick={() => setEnrollGroup(g)}>
                        {t("manageStudents")}
                      </Button>
                    </PermissionGate>
                  </div>
                </CardBody>
              </Card>
            ))}
          </div>
        )}
      </PageSection>

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

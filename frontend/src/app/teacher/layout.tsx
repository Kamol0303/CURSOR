"use client";

import { AuthProvider } from "@/contexts/AuthContext";
import { TeacherLayout } from "@/components/TeacherLayout";

export default function TeacherSectionLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <TeacherLayout>{children}</TeacherLayout>
    </AuthProvider>
  );
}

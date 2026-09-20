import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Breadcrumbs } from './Breadcrumbs';
import { ArchitectureModal } from '../architecture/ArchitectureModal';

export const AppShell: React.FC = () => {
  const [isArchModalOpen, setIsArchModalOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[#F8F7F4] text-[#1F2328]">
      {/* Global Horizontal Header */}
      <Header onOpenArchitecture={() => setIsArchModalOpen(true)} />

      {/* Full-width Main Content Container (no permanent sidebar) */}
      <main className="flex-1 w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
        <Breadcrumbs />
        <Outlet />
      </main>

      {/* Global Architecture Pipeline Modal */}
      <ArchitectureModal
        isOpen={isArchModalOpen}
        onClose={() => setIsArchModalOpen(false)}
      />
    </div>
  );
};

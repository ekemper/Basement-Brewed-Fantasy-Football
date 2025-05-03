import React from "react";
import LegendSection from "./LegendSection";

export default function Dashboard() {
  return (
    <div className="p-8">
      <LegendSection />
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="mt-2 text-gray-600">Welcome to your protected dashboard!</p>
    </div>
  );
} 
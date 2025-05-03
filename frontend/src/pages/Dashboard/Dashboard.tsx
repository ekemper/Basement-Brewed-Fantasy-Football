import React, { useState, useRef } from "react";
import PlayerColumn from "./PlayerColumn";
// @ts-ignore
import heatMapDataRaw from './heat_map_data.json';
import { useOutletContext } from "react-router";

const COLUMN_LABELS: Record<string, string> = {
  A: "COLUMN A: ELITE",
  B: "COLUMN B: FEEL GOOD",
  C: "COLUMN C: FINE",
  D: "COLUMN D: RISKY",
  E: "COLUMN E: DESPERATE",
  F: "COLUMN F: DO NOT PLAY",
};

const COLUMN_KEYS = ["A", "B", "C", "D", "E", "F"] as const;
type ColumnKey = typeof COLUMN_KEYS[number];

interface Player {
  GM: string;
  TM: string;
  POS: string;
  playerName: string;
  playerSummary: string;
}

const heatMapData: Record<ColumnKey, Player[]> = {
  A: heatMapDataRaw.A || [],
  B: heatMapDataRaw.B || [],
  C: heatMapDataRaw.C || [],
  D: heatMapDataRaw.D || [],
  E: heatMapDataRaw.E || [],
  F: heatMapDataRaw.F || [],
};

const COLUMN_HEADER_COLORS: Record<ColumnKey, string> = {
  A: "bg-green-300 dark:bg-green-700 text-black dark:text-white",
  B: "bg-yellow-200 dark:bg-yellow-600 text-black dark:text-white",
  C: "bg-orange-200 dark:bg-orange-600 text-black dark:text-white",
  D: "bg-red-200 dark:bg-red-600 text-black dark:text-white",
  E: "bg-gray-200 dark:bg-gray-700 text-black dark:text-white",
  F: "bg-gray-400 dark:bg-gray-900 text-black dark:text-white",
};

function PlayerSummaryColumn({ summary }: { summary: string }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] shadow-sm max-w-2xl mx-auto mb-8 p-6 min-h-[200px]">
      <div className="whitespace-pre-line text-gray-800 dark:text-gray-100">
        {summary || "Select a player to see their summary."}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { search, setSearch } = useOutletContext<{ search: string; setSearch: (v: string) => void }>();
  const [selectedColumn, setSelectedColumn] = useState<ColumnKey>("A");
  const [selectedPlayerIndex, setSelectedPlayerIndex] = useState<number | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);

  // Flatten all players with their column and index for search
  const allPlayers: { player: Player; column: ColumnKey; index: number }[] = COLUMN_KEYS.flatMap((col) =>
    (heatMapData[col] || []).map((player, idx) => ({ player, column: col, index: idx }))
  );
  const filteredPlayers =
    search.trim() === ""
      ? []
      : allPlayers.filter(({ player }) =>
          player.playerName.toLowerCase().includes(search.trim().toLowerCase())
        );

  const players = heatMapData[selectedColumn] || [];
  const selectedPlayer =
    selectedPlayerIndex !== null && players[selectedPlayerIndex]
      ? players[selectedPlayerIndex]
      : null;
  const selectedSummary = selectedPlayer ? selectedPlayer.playerSummary : "";

  return (
    <div className="p-4 flex flex-col items-center">
      <div className="w-full max-w-6xl rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] shadow-sm p-3 mt-8 pt-2">
        {/* Tabs */}
        <ul className="flex gap-1 justify-center border-b border-gray-200 dark:border-gray-700 mb-4 text-sm">
          {COLUMN_KEYS.map((col) => (
            <li key={col}>
              <button
                className={`px-3 py-1.5 -mb-px font-semibold border-b-2 transition-colors focus:outline-none ${
                  selectedColumn === col
                    ? "border-green-500 text-green-700 dark:text-green-300"
                    : "border-transparent text-gray-700 dark:text-gray-300 hover:text-green-600"
                }`}
                onClick={() => {
                  setSelectedColumn(col);
                  setSelectedPlayerIndex(null);
                }}
              >
                {COLUMN_LABELS[col].replace(/^COLUMN [A-F]: /, "")}
              </button>
            </li>
          ))}
        </ul>
        {/* Player Search Dropdown */}
        {search.trim() !== "" && filteredPlayers.length > 0 && (
          <div className="mb-3 relative w-full max-w-md mx-auto">
            <ul className="absolute z-10 w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 mt-1 rounded shadow-lg max-h-48 overflow-y-auto text-sm">
              {filteredPlayers.map(({ player, column, index }) => (
                <li
                  key={`${column}-${index}`}
                  className="px-3 py-1.5 cursor-pointer hover:bg-green-100 dark:hover:bg-green-900"
                  onMouseDown={() => {
                    setSelectedColumn(column);
                    setSelectedPlayerIndex(index);
                    setSearch("");
                    setShowDropdown(false);
                    if (searchRef.current) searchRef.current.blur();
                  }}
                >
                  {player.playerName} <span className="text-xs text-gray-400 ml-2">({COLUMN_LABELS[column].replace(/^COLUMN [A-F]: /, "")})</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="flex flex-col md:flex-row gap-4 items-start">
          <div className="w-full md:w-1/2">
            <div className="flex flex-col h-full">
              <div className="flex-1 flex flex-col justify-start">
                <div className="flex items-center h-[40px] mb-2">
                  <h2 className={`text-center py-2 text-lg font-bold tracking-wide w-full leading-tight ${COLUMN_HEADER_COLORS[selectedColumn]}`}>
                    {COLUMN_LABELS[selectedColumn] || `COLUMN ${selectedColumn}`}
                  </h2>
                </div>
                <PlayerColumn
                  players={players}
                  title=""
                  onPlayerClick={setSelectedPlayerIndex}
                  selectedIndex={selectedPlayerIndex}
                />
              </div>
            </div>
          </div>
          <div className="w-full md:w-1/2">
            <div className="flex flex-col h-full">
              <div className="flex-1 flex flex-col justify-start">
                <div className="flex items-center h-[40px] mb-2">
                  <h2 className="text-center bg-blue-300 dark:bg-blue-700 text-black dark:text-white py-2 text-lg font-bold tracking-wide w-full leading-tight">
                    Player Summary{selectedPlayer ? `: ${selectedPlayer.playerName}` : ""}
                  </h2>
                </div>
                <PlayerSummaryColumn summary={selectedSummary} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
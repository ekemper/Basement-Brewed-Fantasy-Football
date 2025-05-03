import React, { useRef, useEffect } from 'react';

interface Player {
  GM: string | number;
  TM: string;
  POS: string;
  playerName: string;
  playerSummary: string;
}

interface PlayerColumnProps {
  players: Player[];
  title: string;
  onPlayerClick?: (index: number) => void;
  selectedIndex?: number | null;
}

const PlayerColumn: React.FC<PlayerColumnProps> = ({ players, title, onPlayerClick, selectedIndex }) => {
  const rowRefs = useRef<(HTMLTableRowElement | null)[]>([]);
  const scrollContainerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (
      selectedIndex !== null &&
      selectedIndex !== undefined &&
      rowRefs.current[selectedIndex] &&
      scrollContainerRef.current
    ) {
      const row = rowRefs.current[selectedIndex];
      const container = scrollContainerRef.current;
      if (row && container) {
        const rowTop = row.offsetTop;
        container.scrollTo({ top: rowTop, behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  return (
    <div>
      <p className="mb-2 text-gray-700 dark:text-gray-200">
        <strong>I&apos;d feel good</strong> about having these guys in my lineup. <strong>Something</strong> is preventing them from being Column A, but they&apos;re still set up for a pleasing performance. Players with a <span className="text-blue-600 font-semibold">blue dot</span> are right on the cusp of being promoted to Column A. Players with a <span className="text-yellow-500 font-semibold">yellow dot</span> are right on the cusp of being demoted to Column C.
      </p>
      <p className="mb-4 text-gray-700 dark:text-gray-200">
        <strong>Double click on the player&apos;s name (or press "enter") to read their analysis!</strong>
      </p>
      <div ref={scrollContainerRef} className="overflow-y-auto max-h-[420px]">
        <table className="min-w-full border-collapse rounded-xl overflow-hidden">
          <thead>
            <tr className="bg-green-300 dark:bg-green-700 text-black dark:text-white">
              <th className="py-2 px-3 font-semibold">GM</th>
              <th className="py-2 px-3 font-semibold">TM</th>
              <th className="py-2 px-3 font-semibold">POS</th>
              <th className="py-2 px-3 font-semibold">PLAYER</th>
            </tr>
          </thead>
          <tbody>
            {players.map((row, index) => (
              <tr
                key={index}
                ref={el => { rowRefs.current[index] = el; }}
                className={`text-center border-b border-gray-100 dark:border-gray-800 last:border-b-0 ${onPlayerClick ? 'cursor-pointer hover:bg-green-100 dark:hover:bg-green-900' : ''} ${selectedIndex === index ? 'bg-green-100 dark:bg-green-900' : ''}`}
                onClick={onPlayerClick ? () => onPlayerClick(index) : undefined}
              >
                <td className="py-2 px-3">{row.GM}</td>
                <td className="py-2 px-3">{row.TM}</td>
                <td className="py-2 px-3">{row.POS}</td>
                <td className="py-2 px-3">{row.playerName}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PlayerColumn; 
import React from 'react';

const legends = [
  {
    title: 'O/U (OVER / UNDER)',
    description: 'Estimated combined scores of the two teams.',
    note: 'Lowest total of all games = ',
    red: 'red',
    green: 'green',
    labelLeft: 'Lowest',
    labelRight: 'Highest',
    gradient: ['#d87b7b', '#e8b0b0', '#cde2cd', '#98d798'],
  },
  {
    title: 'SPREAD',
    description: 'Projected point differential between teams.',
    note: 'Underdog = ',
    red: 'red',
    green: 'green',
    labelLeft: 'Underdog',
    labelRight: 'Favored',
    gradient: ['#d87b7b', '#e8b0b0', '#cde2cd', '#98d798'],
  },
  {
    title: 'IMPLIED',
    description: 'Implied estimated score.',
    note: 'Lowest point total of all teams = ',
    red: 'red',
    green: 'green',
    labelLeft: 'Lowest',
    labelRight: 'Highest',
    gradient: ['#d87b7b', '#e8b0b0', '#cde2cd', '#98d798'],
  },
  {
    title: 'QB / RB / WR / TE',
    description: 'Rank of average PPR points allowed to each position.',
    note: 'Easiest matchup = ',
    red: 'red',
    green: 'green',
    labelLeft: 'Easiest',
    labelRight: 'Toughest',
    gradient: ['#89e789', '#d6ff5f', '#ffe761', '#ffc24c', '#e47f7f'],
  },
];

export default function LegendSection() {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white dark:border-gray-800 dark:bg-white/[0.03] shadow-sm max-w-2xl mx-auto mb-8">
      <div className="bg-gray-100 dark:bg-gray-800 px-6 py-3 rounded-t-2xl border-b border-gray-200 dark:border-gray-800 font-semibold text-lg text-gray-800 dark:text-white">
        LEGEND
      </div>
      <div className="divide-y divide-gray-100 dark:divide-gray-800">
        {legends.map((item, i) => (
          <div key={i} className="flex flex-col sm:flex-row items-center gap-4 px-6 py-5">
            <div className="flex-1 w-full">
              <div className="font-semibold text-gray-800 dark:text-white text-base mb-0.5">{item.title}</div>
              <div className="text-gray-600 dark:text-gray-300 text-sm">{item.description}</div>
              <div className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {item.note}
                <span className="font-semibold text-red-500">{item.red}</span>;
                {' '}
                {item.title === 'QB / RB / WR / TE' ? 'toughest matchup = ' : 'highest = '}
                <span className="font-semibold text-green-600">{item.green}</span>.
              </div>
            </div>
            <div className="flex flex-col items-center min-w-[120px]">
              <div className="flex gap-1 mb-1">
                {item.gradient.map((color, index) => (
                  <div key={index} className="w-5 h-5 rounded border border-gray-200 dark:border-gray-700" style={{ backgroundColor: color }} />
                ))}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <span>{item.labelLeft}</span>
                {' ——— '}
                <span>{item.labelRight}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 
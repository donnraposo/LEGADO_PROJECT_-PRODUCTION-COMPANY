interface IconProps {
  name: "archive" | "building" | "chevron" | "close" | "folder" | "grid" | "home" | "logout" | "menu" | "plus" | "search" | "send";
  size?: number;
}

const paths: Record<IconProps["name"], React.ReactNode> = {
  archive: <><path d="M4 7h16"/><path d="M5 7l1 13h12l1-13"/><path d="M9 11h6"/><path d="M5 4h14l1 3H4z"/></>,
  building: <><path d="M4 21V4h11v17"/><path d="M15 9h5v12"/><path d="M8 8h3M8 12h3M8 16h3M3 21h18"/></>,
  chevron: <path d="m9 18 6-6-6-6"/>,
  close: <path d="M18 6 6 18M6 6l12 12"/>,
  folder: <path d="M3 6h7l2 2h9v11H3z"/>,
  grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  home: <><path d="m3 11 9-8 9 8"/><path d="M5 10v11h14V10M9 21v-7h6v7"/></>,
  logout: <><path d="M10 17l5-5-5-5M15 12H3"/><path d="M14 4h6v16h-6"/></>,
  menu: <path d="M4 7h16M4 12h16M4 17h16"/>,
  plus: <path d="M12 5v14M5 12h14"/>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  send: <><path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/></>,
};

export function Icon({ name, size = 18 }: IconProps) {
  return (
    <svg aria-hidden="true" className="ui-icon" fill="none" height={size} viewBox="0 0 24 24" width={size}>
      <g stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.7">{paths[name]}</g>
    </svg>
  );
}

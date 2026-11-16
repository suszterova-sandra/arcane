import { type CSSProperties } from "react";
import { agentAccess, useApp } from "../AppContext";
import { agentStyle, SKILL_LABEL } from "../constants";
import { Icon, type IconName } from "../icons";
import { logoTile, themeVars } from "../theme";
import type { OverviewWorkspace, Persona, TierKey } from "../types";

/** client_id (workspace data filter value) -> name */
const CLIENT_NAMES: Record<string, string> = {
  secondevie: "Seconde Vie",
  autonova: "AutoNova Automobiles",
  routeo: "Routéo Location",
};
const clientName = (id: string) => CLIENT_NAMES[id] || id;

const TIERS: { key: Exclude<TierKey, "admin">; title: string; what: string; isolation: string; can: string }[] = [
  {
    key: "ai",
    title: "Top Account",
    what: "Own workspace in the client's brand. Core + Standard data products plus premium add-ons (product feed, CRM & offline sales, incrementality).",
    isolation: "Workspace data filter = this client only",
    can: "ANALYZE / EXPORT + AI Assistant, per user",
  },
  {
    key: "base",
    title: "Standard",
    what: "Long-tail client on the standard schema: own workspace and brand, Core + Standard data products; premium add-ons are an upsell.",
    isolation: "Workspace data filter = this client only",
    can: "VIEW + AI Assistant",
  },
];

const LAYERS: { icon: IconName; title: string; question: string; how: string; example: string }[] = [
  { icon: "shield", title: "Client", question: "Whose data?", how: "Workspace data filter on wdf__client_id, one client workspace each", example: "Léa sees only Seconde Vie, Elena only Routéo" },
  { icon: "dashboard", title: "Data product × package", question: "Which dashboards, reports, metrics?", how: "Object-level permissions per data-product user group, granted once on the template", example: "Routéo (Standard) has no CRM, Product Feed or Measurement" },
  { icon: "sparkles", title: "Permissions", question: "What can they do?", how: "Workspace permissions VIEW / ANALYZE / EXPORT / AI", example: "Elena views, Marc builds his own analyses; everyone has AI" },
  { icon: "tag", title: "Client definitions", question: "What does 'sales' mean?", how: "AI memory per client workspace on top of Arcane's shared rules", example: "AutoNova: sale = car sold · Routéo: sale = confirmed booking" },
  { icon: "lock", title: "Arcane internal", question: "What stays inside Arcane?", how: "Internal data product, Arcane groups only", example: "Data-request backlog and entitlements: Arcane team only" },
];

const has = (perms: string[], ...want: string[]) => perms.includes("MANAGE") || want.some((w) => perms.includes(w));

function Check({ on, label }: { on: boolean; label?: string }) {
  return on ? <span className="cc-yes" title={label}>✓</span> : <span className="cc-no" title={label}>—</span>;
}

function WsCard({ w, isParent, users }: { w: OverviewWorkspace; isParent?: boolean; users: Persona[] }) {
  const { overview, navigate } = useApp();
  const t = w.themeId ? overview.themes[w.themeId] : undefined;
  const v = themeVars(t);
  const style = {
    "--t-bg": v["--ws-surface"],
    "--t-text": v["--ws-text"],
    "--t-muted": v["--ws-muted"],
    "--t-panel": v["--ws-panel"],
    "--t-line": v["--ws-line"],
    "--t-primary": v["--ws-primary"],
  } as CSSProperties;
  const clients = overview.wdfs.flatMap((f) => f.values[w.id] || []);

  return (
    <button className={`ws-card ${isParent ? "parent" : ""}`} style={style} onClick={() => navigate({ view: "ws", ws: w.id, tab: "home" })}>
      <div className="band" style={t?.cover ? { backgroundImage: `url('${t.cover}')` } : undefined}>
        <div className={`logo ${t?.logo ? "" : "dark"}`} style={{ background: logoTile(t) }}>
          {t?.logo ? <img src={t.logo} alt="" /> : <span style={{ color: v["--ws-primary"], fontWeight: 800 }}>GD</span>}
        </div>
      </div>
      <div className="body">
        <div className="t">{w.name.split(" · ")[0]}</div>
        <div className="s">
          <code>{w.id.length > 20 ? "parent" : w.id}</code> · {w.dashboards.length} dashboards {isParent ? "authored here" : "inherited"}
        </div>
        <dl className="kv">
          <dt>{isParent ? "Data" : clients.length > 1 ? "Clients" : "Client"}</dt>
          <dd>
            {isParent ? <span className="tchip">All clients, unfiltered</span> : clients.map((c) => <span key={c} className="tchip">{clientName(c)}</span>)}
          </dd>
          <dt>Users</dt>
          <dd className="people">
            {users.length ? (
              users.map((p) => (
                <span key={p.id} className={`avatar sm ${p.tierKey}`} title={`${p.name} · ${p.role}`}>
                  {p.initials}
                </span>
              ))
            ) : (
              <span className="tchip">{isParent ? "Arcane team" : "—"}</span>
            )}
          </dd>
        </dl>
      </div>
    </button>
  );
}

export function ControlCenter() {
  const { overview: o, personas, personaWsPerms, groupName, switchPersona, toast } = useApp();
  const parent = o.workspaces.find((w) => w.isParent);
  const users = personas.filter((p) => p.id !== "admin");
  const team = personas.filter((p) => p.tierKey === "admin");
  const usersIn = (wsId: string) => users.filter((p) => p.workspace === wsId);
  const tierOf = (w: OverviewWorkspace) => usersIn(w.id)[0]?.tierKey;
  const children = o.workspaces.filter((w) => !w.isParent).sort((a, b) => a.name.localeCompare(b.name));
  const unused = children.filter((w) => !tierOf(w));
  const featured = o.agents.filter((a) => a.conference);
  const permsOf = (p: Persona) => {
    const live = personaWsPerms(p.id, p.workspace);
    return live.length ? live : p.permissions;
  };

  return (
    <div className="page cc">
      <section className="cc-hero">
        <div>
          <div className="chip glass" style={{ marginBottom: 10 }}>Arcane internal · admin view</div>
          <h1>One template, every client</h1>
          <p>
            One shared data model, 8 data-product dashboards and publisher reports are built once in the Arcane template and inherited by every client
            workspace. The client's package decides which data products it gets; data filters, permissions and the client's own AI definitions decide what
            each user sees.
          </p>
        </div>
        <div className="stats">
          <div className="stat"><b>8</b><span>data products</span></div>
          <div className="stat"><b>{children.length - unused.length}</b><span>client workspaces</span></div>
          <div className="stat"><b>{Object.keys(CLIENT_NAMES).length}</b><span>clients</span></div>
          <div className="stat"><b>{users.length}</b><span>demo users</span></div>
        </div>
      </section>

      <div className="section-title">
        <h2>1 · Workspaces by package</h2>
        <span className="muted small">Click a workspace to open it as admin. Switch user at the top to see it as that user.</span>
      </div>
      <div className="cc-template">
        {parent && <WsCard w={parent} isParent users={team} />}
        <div className="cc-template-note">
          <b>Template (parent workspace)</b>
          <p>Shared data model, metrics, 8 dashboards and 8 publisher reports (one per data product). Arcane team only; no client data filter, all clients side by side.</p>
        </div>
      </div>
      <div className="cc-lanes">
        {TIERS.map((tier) => {
          const wss = children.filter((w) => tierOf(w) === tier.key);
          return (
            <div key={tier.key} className={`cc-lane ${tier.key}`}>
              <div className="cc-lane-h">
                <span className={`tier-badge ${tier.key}`}>{tier.title}</span>
                <p>{tier.what}</p>
                <dl>
                  <dt>Isolation</dt>
                  <dd>{tier.isolation}</dd>
                  <dt>Permissions</dt>
                  <dd>{tier.can}</dd>
                </dl>
              </div>
              {wss.map((w) => (
                <WsCard key={w.id} w={w} users={usersIn(w.id)} />
              ))}
            </div>
          );
        })}
      </div>
      {unused.length > 0 && (
        <p className="muted small" style={{ margin: "10px 2px 0" }}>
          Not used in this demo: {unused.map((w) => w.name).join(", ")} (not part of this demo).
        </p>
      )}

      <div className="section-title">
        <h2>2 · Five access layers</h2>
        <span className="muted small">Every workspace uses the same layers. All are enforced by GoodData, not by this app.</span>
      </div>
      <div className="cc-layers">
        {LAYERS.map((l) => (
          <div key={l.title} className="card cc-layer">
            <div className="cc-layer-h">
              <Icon name={l.icon} size={16} /> <b>{l.title}</b>
            </div>
            <div className="cc-layer-q">{l.question}</div>
            <div className="cc-layer-how">{l.how}</div>
            <div className="muted small">{l.example}</div>
          </div>
        ))}
      </div>

      <div className="section-title">
        <h2>3 · Who sees what</h2>
        <span className="muted small">One row per user, as GoodData resolves it. “View as” switches to that user.</span>
      </div>
      <div className="card">
        <table className="matrix cc-who">
          <thead>
            <tr>
              <th>User</th>
              <th>Workspace</th>
              <th>Client data</th>
              <th>Markets</th>
              <th>Data products (dashboards)</th>
              <th className="c">Build own</th>
              <th className="c">AI</th>
              <th className="c">Arcane internal</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {[...team.filter((p) => p.id !== "admin"), ...TIERS.flatMap((tier) => users.filter((p) => p.tierKey === tier.key))].map((p) => {
              const perms = permsOf(p);
              const internal = p.tierKey === "admin";
              return (
                <tr key={p.id}>
                  <td>
                    <div className="who">
                      <span className={`avatar ${p.tierKey}`}>{p.initials}</span>
                      <div>
                        <b>{p.name}</b>
                        <small>{p.role.split(" · ")[0]}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={`tier-badge ${p.tierKey}`}>{p.tier}</span>
                    <small className="cc-sub"><code>{p.workspace}</code></small>
                  </td>
                  <td>
                    <b>{p.client}</b>
                    <small className="cc-sub">{internal ? "all clients (template)" : "own client workspace only"}</small>
                  </td>
                  <td>{p.locations.join(", ")}</td>
                  <td>
                    <div className="cc-products">
                      {p.products.map((x) => (
                        <span key={x} className="chip muted">{x}</span>
                      ))}
                    </div>
                  </td>
                  <td className="c"><Check on={has(perms, "ANALYZE")} label="ANALYZE" /></td>
                  <td className="c"><Check on={has(perms, "USE_AI_ASSISTANT")} label="USE_AI_ASSISTANT" /></td>
                  <td className="c"><Check on={p.products.includes("Arcane Operations")} label="Arcane Operations data product" /></td>
                  <td>
                    <button
                      className="btn"
                      disabled={!p.available}
                      onClick={() => switchPersona(p.id, null).then(() => toast(`Now viewing as ${p.name}`))}
                    >
                      View as →
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="section-title">
        <h2>4 · AI agents</h2>
        <span className="muted small">Configured once in AI Hub and assigned to user groups: every client with the data product (and the Arcane team) can use them.</span>
      </div>
      <div className="card">
        <table className="matrix">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Skills</th>
              <th>Assigned to</th>
              {personas.map((p) => (
                <th key={p.id} className="c" title={`${p.name} · ${p.tier}`}>
                  <span className={`avatar sm ${p.tierKey}`} style={{ margin: "0 auto" }}>{p.initials}</span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {featured.map((a) => {
              const st = agentStyle(a.id);
              return (
                <tr key={a.id}>
                  <td>
                    <div className="agent-name">
                      <span className="ico" style={{ background: st.bg, color: st.fg }}><Icon name={st.ico} size={16} /></span>
                      <div>
                        <b>{a.name}</b>
                        <div className="muted small" style={{ maxWidth: 320 }}>{a.description}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div className="skills">
                      {(a.skills || []).slice(0, 4).map((s) => (
                        <span key={s} className="skill">{SKILL_LABEL[s] || s}</span>
                      ))}
                    </div>
                  </td>
                  <td>
                    {a.availableToAll ? (
                      <span className="chip ok">Everyone</span>
                    ) : (
                      a.groups.map((g) => (
                        <span key={g} className="chip muted" style={{ marginRight: 4 }}>{groupName(g)}</span>
                      ))
                    )}
                  </td>
                  {personas.map((p) => (
                    <td key={p.id} className="c">
                      <Check on={agentAccess(o, a, p.id)} />
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div style={{ height: 40 }} />
    </div>
  );
}

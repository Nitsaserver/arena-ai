import React, { useEffect, useState } from "react";
import { fetchMatches, createMatch, deleteMatch } from "../api";

interface Match {
  id: number;
  team_a: string;
  team_b: string;
  score: string;
}

const MatchesTable: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [newMatch, setNewMatch] = useState({ team_a: "", team_b: "", score: "" });

  useEffect(() => {
    const getMatches = async () => {
      try {
        const data = await fetchMatches();
        setMatches(data);
      } catch (err) {
        console.error("Error fetching matches:", err);
      } finally {
        setLoading(false);
      }
    };
    getMatches();
  }, []);

  const handleCreate = async () => {
    if (!newMatch.team_a || !newMatch.team_b || !newMatch.score)
      return alert("All fields required");
    const res = await createMatch(newMatch);
    setMatches([...matches, res.match]);
    setNewMatch({ team_a: "", team_b: "", score: "" });
  };

  const handleDelete = async (id: number) => {
    await deleteMatch(id);
    setMatches(matches.filter((m) => m.id !== id));
  };

  if (loading) return <p>Loading matches...</p>;

  return (
    <div>
      <h2>Matches</h2>
      <div style={{ marginBottom: "10px" }}>
        <input
          placeholder="Team A"
          value={newMatch.team_a}
          onChange={(e) => setNewMatch({ ...newMatch, team_a: e.target.value })}
        />
        <input
          placeholder="Team B"
          value={newMatch.team_b}
          onChange={(e) => setNewMatch({ ...newMatch, team_b: e.target.value })}
        />
        <input
          placeholder="Score"
          value={newMatch.score}
          onChange={(e) => setNewMatch({ ...newMatch, score: e.target.value })}
        />
        <button onClick={handleCreate}>Add Match</button>
      </div>

      <table border={1} cellPadding={8} style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr><th>ID</th><th>Team A</th><th>Team B</th><th>Score</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {matches.map((m) => (
            <tr key={m.id}>
              <td>{m.id}</td>
              <td>{m.team_a}</td>
              <td>{m.team_b}</td>
              <td>{m.score}</td>
              <td><button onClick={() => handleDelete(m.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MatchesTable;

import React from "react";
import UsersTable from "../components/UsersTable";

const UsersPage: React.FC = () => {
  return (
    <div style={{ padding: "20px" }}>
      <h2>Users</h2>
      <UsersTable />
    </div>
  );
};

export default UsersPage; // 👈 THIS LINE is crucial

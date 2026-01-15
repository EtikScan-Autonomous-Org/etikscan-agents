import React from 'react';
import OrganizationSettings from './OrganizationSettings';
import ApiTokens from '../tokens/ApiTokens';

const SettingsPage: React.FC = () => {
  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>Settings</h1>
        <p>Manage your organization settings and API tokens for Terraform integration.</p>
      </div>
      
      <div className="settings-container">
        <OrganizationSettings />
        
        <div className="divider" />
        
        <ApiTokens />
      </div>
      
      <div className="settings-help">
        <h2>Need Help?</h2>
        <p>
          For more information on using Tembo with Terraform, refer to the 
          <a href="https://docs.tembo.io/terraform" target="_blank" rel="noopener noreferrer">
            Tembo Terraform documentation
          </a>.
        </p>
      </div>
    </div>
  );
};

export default SettingsPage;
import React, { useEffect, useState } from 'react';
import { getOrganization } from '../../services/api';
import { Organization } from '../../types';

const OrganizationSettings: React.FC = () => {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrganizationData = async () => {
      try {
        setLoading(true);
        const orgData = await getOrganization();
        setOrganization(orgData);
        setError(null);
      } catch (err) {
        setError('Failed to fetch organization details. Please try again later.');
        console.error('Error fetching organization:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizationData();
  }, []);

  if (loading) {
    return <div className="loading">Loading organization details...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="organization-settings">
      <div className="settings-section">
        <h2>Organization Details</h2>
        <div className="info-card">
          {organization ? (
            <>
              <div className="info-row">
                <div className="label">Organization Name:</div>
                <div className="value">{organization.name}</div>
              </div>
              <div className="info-row highlight">
                <div className="label">Organization ID:</div>
                <div className="value id-display">
                  <code>{organization.id}</code>
                  <button 
                    className="copy-button"
                    onClick={() => {
                      navigator.clipboard.writeText(organization.id);
                      // Could add toast notification here
                    }}
                  >
                    Copy
                  </button>
                </div>
              </div>
              <div className="info-row">
                <div className="label">Created:</div>
                <div className="value">{new Date(organization.createdAt).toLocaleDateString()}</div>
              </div>
              <div className="terraform-help">
                <h3>Using with Terraform</h3>
                <p>
                  Use this Organization ID with the Tembo Terraform provider:
                </p>
                <pre>
{`provider "tembo" {
  org_id = "${organization?.id}"
  api_token = "your-api-token" # Create an API token below
}`}
                </pre>
              </div>
            </>
          ) : (
            <div className="no-data">Organization information not available</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default OrganizationSettings;
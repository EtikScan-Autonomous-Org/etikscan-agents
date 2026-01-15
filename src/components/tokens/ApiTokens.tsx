import React, { useEffect, useState } from 'react';
import { getApiTokens, createApiToken, deleteApiToken } from '../../services/api';
import { ApiToken, CreateApiTokenRequest } from '../../types';

const ApiTokens: React.FC = () => {
  const [tokens, setTokens] = useState<ApiToken[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newTokenName, setNewTokenName] = useState<string>('');
  const [newTokenExpiry, setNewTokenExpiry] = useState<number | null>(90);
  const [newToken, setNewToken] = useState<string | null>(null);
  const [showForm, setShowForm] = useState<boolean>(false);

  // Fetch tokens on component mount
  const fetchTokens = async () => {
    try {
      setLoading(true);
      const tokensData = await getApiTokens();
      setTokens(tokensData);
      setError(null);
    } catch (err) {
      setError('Failed to fetch API tokens. Please try again later.');
      console.error('Error fetching tokens:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTokens();
  }, []);

  // Handle token creation
  const handleCreateToken = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newTokenName.trim()) {
      setError('Token name is required');
      return;
    }

    try {
      setLoading(true);
      const tokenRequest: CreateApiTokenRequest = {
        name: newTokenName.trim(),
        expiresInDays: newTokenExpiry
      };
      
      const response = await createApiToken(tokenRequest);
      
      // Show the newly created token to the user (this is the only time it will be visible)
      setNewToken(response.token.token);
      
      // Reset form and refresh token list
      setNewTokenName('');
      setNewTokenExpiry(90);
      setShowForm(false);
      await fetchTokens();
    } catch (err) {
      setError('Failed to create API token. Please try again.');
      console.error('Error creating token:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle token deletion
  const handleDeleteToken = async (tokenId: string) => {
    if (!window.confirm('Are you sure you want to delete this token? This action cannot be undone.')) {
      return;
    }

    try {
      setLoading(true);
      await deleteApiToken(tokenId);
      await fetchTokens();
    } catch (err) {
      setError('Failed to delete API token. Please try again.');
      console.error('Error deleting token:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="api-tokens">
      <div className="tokens-header">
        <h2>API Tokens</h2>
        {!showForm && (
          <button 
            className="create-token-button"
            onClick={() => setShowForm(true)}
          >
            Create New Token
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {/* Display newly created token */}
      {newToken && (
        <div className="new-token-alert">
          <h3>New API Token Created</h3>
          <p className="warning">This token will only be displayed once. Please copy it now.</p>
          <div className="token-display">
            <code>{newToken}</code>
            <button 
              className="copy-button"
              onClick={() => {
                navigator.clipboard.writeText(newToken);
                // Could add toast notification here
              }}
            >
              Copy
            </button>
          </div>
          <div className="terraform-example">
            <h4>Example Terraform Configuration</h4>
            <pre>
{`provider "tembo" {
  org_id = "your-org-id" # From Organization Settings
  api_token = "${newToken}"
}`}
            </pre>
          </div>
          <button 
            className="dismiss-button"
            onClick={() => setNewToken(null)}
          >
            I've copied my token
          </button>
        </div>
      )}

      {/* Token creation form */}
      {showForm && (
        <form className="token-form" onSubmit={handleCreateToken}>
          <h3>Create New API Token</h3>
          <div className="form-group">
            <label htmlFor="tokenName">Token Name</label>
            <input
              id="tokenName"
              type="text"
              value={newTokenName}
              onChange={(e) => setNewTokenName(e.target.value)}
              placeholder="e.g., Terraform Production"
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="tokenExpiry">Expiration</label>
            <select
              id="tokenExpiry"
              value={newTokenExpiry === null ? 'never' : newTokenExpiry.toString()}
              onChange={(e) => {
                const value = e.target.value;
                setNewTokenExpiry(value === 'never' ? null : parseInt(value, 10));
              }}
            >
              <option value="30">30 days</option>
              <option value="60">60 days</option>
              <option value="90">90 days</option>
              <option value="180">180 days</option>
              <option value="365">365 days</option>
              <option value="never">Never expires</option>
            </select>
          </div>
          <div className="form-actions">
            <button 
              type="button" 
              className="cancel-button"
              onClick={() => {
                setShowForm(false);
                setNewTokenName('');
                setNewTokenExpiry(90);
              }}
            >
              Cancel
            </button>
            <button 
              type="submit"
              className="submit-button"
              disabled={loading || !newTokenName.trim()}
            >
              {loading ? 'Creating...' : 'Create Token'}
            </button>
          </div>
        </form>
      )}

      {/* Existing tokens list */}
      <div className="tokens-list">
        <h3>Your API Tokens</h3>
        {loading && !tokens.length ? (
          <div className="loading">Loading tokens...</div>
        ) : !tokens.length ? (
          <div className="no-tokens">No API tokens found. Create a token to use with Terraform.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Created</th>
                <th>Expires</th>
                <th>Last Used</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {tokens.map((token) => (
                <tr key={token.id}>
                  <td>{token.name}</td>
                  <td>{new Date(token.createdAt).toLocaleDateString()}</td>
                  <td>
                    {token.expiresAt 
                      ? new Date(token.expiresAt).toLocaleDateString()
                      : 'Never'}
                  </td>
                  <td>
                    {token.lastUsedAt 
                      ? new Date(token.lastUsedAt).toLocaleDateString()
                      : 'Never used'}
                  </td>
                  <td>
                    <button 
                      className="delete-button"
                      onClick={() => handleDeleteToken(token.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default ApiTokens;
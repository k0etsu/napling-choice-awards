import React, { useState, useEffect } from 'react';
import { Container, Card, Alert, Spinner, Table, ProgressBar } from 'react-bootstrap';
import axios from 'axios';
import './Results.css';

const Results = () => {
  const [categories, setCategories] = useState([]);
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/categories');
      // Filter to only show locked categories
      const lockedCategories = response.data.filter(category => category.voting_locked);
      setCategories(lockedCategories);
      setLoading(false);
    } catch (err) {
      setError('Failed to load categories. Please try again later.');
      setLoading(false);
    }
  };

  const fetchAllResults = async () => {
    const resultsData = {};

    for (const category of categories) {
      try {
        const response = await axios.get(`/api/results/${category.id}`);
        resultsData[category.id] = response.data;
      } catch (err) {
        console.error(`Failed to load results for ${category.name}:`, err);
      }
    }

    setResults(resultsData);
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    // Fetch results for all locked categories
    if (categories.length > 0) {
      fetchAllResults();
    }
  }, [categories]);

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" className="loading-spinner" />
        <p className="mt-3">Loading results...</p>
      </Container>
    );
  }

  return (
    <Container>
      <div className="text-center mb-5">
        <h1 className="display-4">Voting Results</h1>
        <p className="lead">View voting results for locked categories</p>
      </div>

      <div className="floating-alerts">
        {error && <Alert variant="danger">{error}</Alert>}
      </div>

      {categories.length > 0 ? (
        categories.map((category) => (
          <Card key={category.id} className="mb-4">
            <Card.Header>
              <h4 className="mb-0">{category.name}</h4>
            </Card.Header>
            <Card.Body>
              {results[category.id] && results[category.id].length > 0 ? (
                <>
                  {/* Display winning product image if available */}
                    <div className="text-center mb-4">
                      {results[category.id][0]?.product?.image_url && (
                        <img
                          src={results[category.id][0].product.image_url}
                          alt={results[category.id][0].product.name}
                          className="winner-image mb-3"
                        />
                      )}
                      <h4 className="mt-2 winner-title">
                        🏆 Winner: {results[category.id][0].product.name}
                      </h4>
                    </div>

                  <Table striped bordered hover className="results-table">
                  <thead>
                    <tr>
                      <th>Product</th>
                      <th style={{ width: '80px' }}>Votes</th>
                      <th style={{ width: '50%' }}>Vote Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results[category.id].map((result, index) => {
                      const maxVotes = Math.max(...results[category.id].map(r => r.vote_count));
                      const percentage = maxVotes > 0 ? (result.vote_count / maxVotes) * 100 : 0;

                      return (
                        <tr key={result.product_id}>
                          <td>
                            <strong>{result.product?.name || 'Unknown Product'}</strong>
                          </td>
                          <td style={{ width: '80px' }}>
                            <span className="badge bg-success">
                              {result.vote_count} vote{result.vote_count !== 1 ? 's' : ''}
                            </span>
                          </td>
                          <td style={{ width: '50%' }}>
                            <div className="w-100">
                              <ProgressBar
                                now={percentage}
                                label={`${percentage.toFixed(1)}%`}
                                variant={index === 0 ? 'success' : percentage >= 50 ? 'info' : 'secondary'}
                              />
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </Table>
                </>
              ) : (
                <div className="text-center py-4">
                  <h4>No votes recorded yet</h4>
                  <p className="text-muted">Voting results will appear here once users start voting.</p>
                </div>
              )}
            </Card.Body>
          </Card>
        ))
      ) : (
        <div className="text-center py-5">
          <h3>No locked categories available</h3>
          <p className="text-muted">Results will appear here once categories are locked and voting is complete.</p>
        </div>
      )}
    </Container>
  );
};

export default Results;

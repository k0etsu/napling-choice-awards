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
                  {/* Display winning nominee(s) image(s) if available */}
                    <div className="text-center mb-4">
                      {(() => {
                        const maxVotes = Math.max(...results[category.id].map(r => r.vote_count));
                        const winners = results[category.id].filter(r => r.vote_count === maxVotes);
                        const isTie = winners.length > 1;

                        return (
                          <>
                            {isTie ? (
                              <div className="tie-winners">
                                <h4 className="mt-2 winner-title">
                                  🏆 TIED WINNERS
                                </h4>
                                <div className="d-flex justify-content-center gap-3 flex-wrap">
                                  {winners.map((winner, index) => (
                                    <div key={winner.nominee_id} className="text-center">
                                      {winner.nominee?.image_url && (
                                        <img
                                          src={winner.nominee.image_url}
                                          alt={winner.nominee.name}
                                          className="winner-image mb-2"
                                          style={{ maxWidth: '120px', maxHeight: '120px' }}
                                        />
                                      )}
                                      <div className="fw-bold">{winner.nominee.name}</div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            ) : (
                              <div>
                                {results[category.id][0]?.nominee?.image_url && (
                                  <img
                                    src={results[category.id][0].nominee.image_url}
                                    alt={results[category.id][0].nominee.name}
                                    className="winner-image mb-3"
                                  />
                                )}
                                <h4 className="mt-2 winner-title">
                                  🏆 Winner: {results[category.id][0].nominee.name}
                                </h4>
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>

                  <Table striped bordered hover className="results-table">
                  <thead>
                    <tr>
                      <th>Nominee</th>
                      <th style={{ width: '80px' }}>Votes</th>
                      <th style={{ width: '50%' }}>Vote Percentage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(() => {
                      const maxVotes = Math.max(...results[category.id].map(r => r.vote_count));
                      const winners = results[category.id].filter(r => r.vote_count === maxVotes);
                      const isTie = winners.length > 1;

                      return results[category.id].map((result, index) => {
                        const percentage = maxVotes > 0 ? (result.vote_count / maxVotes) * 100 : 0;
                        const isWinner = result.vote_count === maxVotes;

                        return (
                          <tr key={result.nominee_id}>
                            <td>
                              <strong>{result.nominee?.name || 'Unknown Nominee'}</strong>
                              {isWinner && isTie && (
                                <span className="badge bg-warning ms-2">🏆 TIED</span>
                              )}
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
                                  className={
                                    isWinner
                                      ? isTie
                                        ? 'tie-progress'
                                        : 'winner-progress'
                                      : 'regular-progress'
                                  }
                                />
                              </div>
                            </td>
                          </tr>
                        );
                      });
                    })()}
                  </tbody>
                </Table>
                </>
              ) : (
                <div className="text-center py-4">
                  <h4>No votes recorded yet</h4>
                  <p className="text-muted">Voting results will appear here once users start voting for nominees.</p>
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

import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';
import VideoModal from './VideoModal';
import './Home.css';

const Home = () => {
  const [categories, setCategories] = useState([]);
  const [nominees, setNominees] = useState({});
  const [userVotes, setUserVotes] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedVideo, setSelectedVideo] = useState({ url: '', name: '' });
  const [showVideoModal, setShowVideoModal] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [categoriesRes, nomineesRes] = await Promise.all([
        axios.get('/api/categories'),
        axios.get('/api/nominees')
      ]);

      setCategories(categoriesRes.data);

      // Group nominees by category
      const groupedNominees = {};
      nomineesRes.data.forEach(nominee => {
        if (!groupedNominees[nominee.category_id]) {
          groupedNominees[nominee.category_id] = [];
        }
        groupedNominees[nominee.category_id].push(nominee);
      });
      setNominees(groupedNominees);

      // Fetch user votes for each category
      const votePromises = categoriesRes.data.map(category =>
        axios.get(`/api/vote/${category.id}`).catch((err) => {
          console.log(`Failed to fetch vote for category ${category.id}:`, err);
          return { data: { vote: null } };
        })
      );

      const voteResponses = await Promise.all(votePromises);
      const votes = {};

      voteResponses.forEach((response, index) => {
        const categoryId = categoriesRes.data[index].id;
        console.log(`Category ${categoryId} vote response:`, response.data);

        // Handle both response formats: {vote: voteData} or direct voteData
        if (response.data.vote !== undefined) {
          votes[categoryId] = response.data.vote;
        } else {
          votes[categoryId] = response.data;
        }
      });

      setUserVotes(votes);

      setLoading(false);
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      setLoading(false);
    }
  };

  const handleVote = async (nomineeId, categoryId) => {
    try {
      const category = categories.find(c => c.id === categoryId);
      if (category && category.voting_locked) {
        setError('Voting is locked for this category.');
        setTimeout(() => setError(''), 3000);
        return;
      }

      const response = await axios.post('/api/vote', {
        nominee_id: nomineeId,
        category_id: categoryId
      });

      const isUpdate = response.data.action === 'updated';

      setSuccess(isUpdate ? 'Your vote has been updated!' : 'Your vote has been recorded!');

      // Update user votes state
      setUserVotes(prev => ({
        ...prev,
        [categoryId]: response.data
      }));

      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to cast vote. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleVideoClick = (videoUrl, nomineeName) => {
    setSelectedVideo({ url: videoUrl, name: nomineeName });
    setShowVideoModal(true);
  };

  const handleCloseVideoModal = () => {
    setShowVideoModal(false);
    setSelectedVideo({ url: '', name: '' });
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" className="loading-spinner" />
        <p className="mt-3">Loading categories and nominees...</p>
      </Container>
    );
  }

  return (
    <Container>
      <div className="text-center mb-5">
        <h1 className="display-4">Welcome to Napling Choice Awards</h1>
        <p className="lead">Vote for your favorite nominees in each category</p>
      </div>

      <div className="floating-alerts">
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
      </div>

      {categories.map((category) => (
        <div key={`category-${category.id}`} className="category-section">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h2 className="section-title mb-0">{category.name}</h2>
            <span className={`badge ${category.voting_locked ? 'bg-danger' : 'bg-success'}`}>
              {category.voting_locked ? 'Voting Locked' : 'Voting Open'}
            </span>
          </div>
          {category.description && (
            <p className="text-muted mb-4">{category.description}</p>
          )}

          <Row className="g-3">
            {nominees[category.id]?.map((nominee) => {
              const userVote = userVotes[category.id];
              const isSelected = userVote && userVote.nominee_id === nominee.id;

              return (
                <Col xs={12} sm={6} md={4} lg={3} key={`nominee-${nominee.id}`} className="mb-3">
                  <Card className={`nominee-card h-100 ${isSelected ? 'border-primary border-2' : ''}`}>
                    {nominee.image_url && (
                      <Card.Img
                        variant="top"
                        src={nominee.image_url.startsWith('http') ? nominee.image_url : `http://localhost:5001${nominee.image_url}`}
                        className="nominee-image"
                        alt={nominee.name}
                      />
                    )}
                    <Card.Body className="d-flex flex-column">
                      <Card.Title className="d-flex justify-content-between align-items-start">
                        <span>{nominee.name}</span>
                        <div className="d-flex gap-2">
                          {nominee.youtube_url && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => handleVideoClick(nominee.youtube_url, nominee.name)}
                              className="video-button"
                              title="Watch video"
                            >
                              ▶️
                            </Button>
                          )}
                        </div>
                      </Card.Title>
                      <Card.Text className="flex-grow-1">
                        {nominee.description}
                      </Card.Text>
                      <Button
                        variant={isSelected ? "success" : "primary"}
                        onClick={() => handleVote(nominee.id, category.id)}
                        disabled={category.voting_locked}
                        className="vote-button mt-auto"
                      >
                        {
                          isSelected ?
                            '✓ Voted' :
                            category.voting_locked ?
                              'Voting Locked' :
                              'Vote'
                        }
                      </Button>
                    </Card.Body>
                  </Card>
                </Col>
              );
            })}
          </Row>

          {nominees[category.id]?.length === 0 && (
            <p className="text-muted">No nominees available in this category yet.</p>
          )}
        </div>
      ))}

      {categories.length === 0 && (
        <div className="text-center py-5">
          <h3>No categories available</h3>
          <p>Please check back later or contact an administrator.</p>
        </div>
      )}

      <VideoModal
        show={showVideoModal}
        handleClose={handleCloseVideoModal}
        videoUrl={selectedVideo.url}
        nomineeName={selectedVideo.name}
      />
    </Container>
  );
};

export default Home;

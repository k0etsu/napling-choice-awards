import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Card, Form, Button, Table, Spinner, Alert, Modal, Badge } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

const Admin = () => {
  const [categories, setCategories] = useState([]);
  const [nominees, setNominees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [expandedCategories, setExpandedCategories] = useState(new Set());
  const [currentUser, setCurrentUser] = useState(null);

  // Modal states
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [showNomineeModal, setShowNomineeModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [editingNominee, setEditingNominee] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [imageInputMode, setImageInputMode] = useState('upload'); // 'upload' or 'url'
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [tempImageFile, setTempImageFile] = useState(null);
  const [tempImagePreview, setTempImagePreview] = useState('');

  // Password change form
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('adminToken');
    const user = localStorage.getItem('adminUser');

    if (!token || !user) {
      navigate('/login');
      return;
    }

    // Set up axios interceptor for authentication
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    setCurrentUser(user);

    // Verify token is still valid
    const verifyAuth = async () => {
      try {
        await axios.get('/api/auth/verify');
        fetchData();
      } catch (err) {
        // Token is invalid, redirect to login
        localStorage.removeItem('adminToken');
        localStorage.removeItem('adminUser');
        delete axios.defaults.headers.common['Authorization'];
        navigate('/login');
      }
    };

    verifyAuth();
  }, [navigate]);

  const fetchData = async () => {
    try {
      const [categoriesRes, nomineesRes] = await Promise.all([
        axios.get('/api/categories'),
        axios.get('/api/nominees')
      ]);

      setCategories(categoriesRes.data);
      setNominees(nomineesRes.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      setLoading(false);
    }
  };

  const toggleCategoryExpansion = (categoryId) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleCategoryLock = async (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    if (!category) return;

    try {
      await axios.put(`/api/categories/${categoryId}`, {
        ...category,
        voting_locked: !category.voting_locked
      });
      setSuccess(`Category ${category.voting_locked ? 'unlocked' : 'locked'} successfully!`);
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update category lock status.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const openAddCategoryModal = () => {
    setEditingCategory({
      name: '',
      description: '',
      voting_locked: false,
      isNewCategory: true
    });
    setShowCategoryModal(true);
  };

  const openAddNomineeModal = (categoryId) => {
    setSelectedCategoryId(categoryId);
    setEditingNominee({
      name: '',
      description: '',
      image_url: '',
      youtube_url: '',
      category_id: categoryId,
      isNewNominee: true
    });
    setTempImageFile(null);
    setTempImagePreview('');
    setShowNomineeModal(true);
  };

  const handleUpdateCategory = async (categoryId) => {
    try {
      await axios.put(`/api/categories/${categoryId}`, editingCategory);
      setSuccess('Category updated successfully!');
      setEditingCategory(null);
      setShowCategoryModal(false);
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update category. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleUpdateNominee = async (nomineeId) => {
    try {
      let nomineeData = { ...editingNominee };

      // Upload image if there's a temporary file
      if (tempImageFile) {
        const imageUrl = await uploadImageAndSetUrl(tempImageFile);
        if (imageUrl) {
          nomineeData.image_url = imageUrl;
        } else {
          // If upload fails, don't submit the form
          return;
        }
      }

      await axios.put(`/api/nominees/${nomineeId}`, nomineeData);
      setSuccess('Nominee updated successfully!');
      setShowNomineeModal(false);
      setEditingNominee(null);
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update nominee. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (window.confirm('Are you sure you want to delete this category? This action cannot be undone.')) {
      try {
        await axios.delete(`/api/categories/${categoryId}`);
        setSuccess('Category deleted successfully!');
        setShowCategoryModal(false);
        setEditingCategory(null);
        fetchData();
        setTimeout(() => setSuccess(''), 3000);
      } catch (err) {
        setError('Failed to delete category. Please try again.');
        setTimeout(() => setError(''), 3000);
      }
    }
  };

  const handleDeleteNominee = async (nomineeId) => {
    if (window.confirm('Are you sure you want to delete this nominee? This action cannot be undone.')) {
      try {
        await axios.delete(`/api/nominees/${nomineeId}`);
        setSuccess('Nominee deleted successfully!');
        setShowNomineeModal(false);
        setEditingNominee(null);
        fetchData();
        setTimeout(() => setSuccess(''), 3000);
      } catch (err) {
        setError('Failed to delete nominee. Please try again.');
        setTimeout(() => setError(''), 3000);
      }
    }
  };

  const openCategoryModal = (category = null) => {
    setEditingCategory(category);
    setShowCategoryModal(true);
  };

  const openNomineeModal = (nominee = null) => {
    setEditingNominee(nominee);
    setTempImageFile(null);
    setTempImagePreview('');
    setShowNomineeModal(true);
  };

  const closeCategoryModal = () => {
    setShowCategoryModal(false);
    setEditingCategory(null);
  };

  const closeNomineeModal = () => {
    setShowNomineeModal(false);
    setEditingNominee(null);
    setSelectedCategoryId(null);
    setTempImageFile(null);
    setTempImagePreview('');
  };

  const handleImagePreview = (file) => {
    if (!file) return;

    // Create preview URL for the selected file
    const previewUrl = URL.createObjectURL(file);
    setTempImageFile(file);
    setTempImagePreview(previewUrl);

    // Update the editingNominee with a placeholder that will be replaced on submission
    setEditingNominee(prev => ({
      ...prev,
      image_url: 'temp-preview'
    }));
  };

  const uploadImageAndSetUrl = async (file) => {
    if (!file) return null;

    setUploadingImage(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return response.data.url;
    } catch (err) {
      setError('Failed to upload image. Please try again.');
      setTimeout(() => setError(''), 3000);
      return null;
    } finally {
      setUploadingImage(false);
    }
  };

  const handleCategorySubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/categories', editingCategory);
      setSuccess('Category created successfully!');
      closeCategoryModal();
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to create category. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleNomineeSubmit = async (e) => {
    e.preventDefault();

    try {
      let nomineeData = {
        ...editingNominee,
        category_id: selectedCategoryId
      };

      // Upload image if there's a temporary file
      if (tempImageFile) {
        const imageUrl = await uploadImageAndSetUrl(tempImageFile);
        if (imageUrl) {
          nomineeData.image_url = imageUrl;
        } else {
          // If upload fails, don't submit the form
          return;
        }
      }

      await axios.post('/api/nominees', nomineeData);
      setSuccess('Nominee created successfully!');
      closeNomineeModal();
      fetchData();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to create nominee. Please try again.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('adminToken');
    localStorage.removeItem('adminUser');
    delete axios.defaults.headers.common['Authorization'];
    navigate('/login');
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError('New passwords do not match');
      setTimeout(() => setError(''), 3000);
      return;
    }

    if (passwordForm.new_password.length < 6) {
      setError('New password must be at least 6 characters long');
      setTimeout(() => setError(''), 3000);
      return;
    }

    try {
      await axios.post('/api/auth/change-password', {
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });

      setSuccess('Password changed successfully!');
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
      setShowPasswordModal(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
      setTimeout(() => setError(''), 3000);
    }
  };

  const openPasswordModal = () => {
    setPasswordForm({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
    setShowPasswordModal(true);
  };

  const closePasswordModal = () => {
    setShowPasswordModal(false);
    setPasswordForm({
      current_password: '',
      new_password: '',
      confirm_password: ''
    });
  };

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" className="loading-spinner" />
        <p className="mt-3">Loading admin panel...</p>
      </Container>
    );
  }

  return (
    <Container>
      <div className="text-center mb-5">
        <h1 className="display-4">Admin Panel</h1>
        <p className="lead">Manage categories and nominees</p>
        <div className="d-flex justify-content-center align-items-center gap-3">
          <span className="text-muted">Logged in as: <strong>{currentUser}</strong></span>
          <Button variant="outline-primary" size="sm" onClick={openPasswordModal}>
            Change Password
          </Button>
          <Button variant="outline-danger" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </div>
      </div>

      <div className="floating-alerts">
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
      </div>

      <div className="admin-panel">
        <Card>
          <Card.Header className="d-flex justify-content-between align-items-center">
            <h5 className="mb-0">Categories & Nominees</h5>
            <Button variant="primary" onClick={openAddCategoryModal}>
              Add Category
            </Button>
          </Card.Header>
          <Card.Body>
            {categories.length > 0 ? (
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th width="30"></th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Voting Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.map((category) => {
                    const categoryNominees = nominees.filter(n => n.category_id === category.id);
                    const isExpanded = expandedCategories.has(category.id);

                    return (
                      <React.Fragment key={category.id}>
                        <tr>
                          <td className="text-center">
                            <Button
                              variant="outline-secondary"
                              size="sm"
                              onClick={() => toggleCategoryExpansion(category.id)}
                              style={{ width: '30px' }}
                            >
                              {isExpanded ? '-' : '+'}
                            </Button>
                          </td>
                          <td>
                            <strong>{category.name}</strong>
                            {categoryNominees.length > 0 && (
                              <div className="text-muted small">
                                {categoryNominees.length} nominee{categoryNominees.length !== 1 ? 's' : ''}
                              </div>
                            )}
                          </td>
                          <td>{category.description || '-'}</td>
                          <td>
                            <Badge
                              bg={category.voting_locked ? 'danger' : 'success'}
                              style={{ cursor: 'pointer' }}
                              onClick={() => toggleCategoryLock(category.id)}
                              title="Click to toggle lock status"
                            >
                              {category.voting_locked ? 'Locked' : 'Open'}
                            </Badge>
                          </td>
                          <td>
                            <Button
                              variant="primary"
                              size="sm"
                              className="me-2"
                              onClick={() => openCategoryModal(category)}
                            >
                              Edit
                            </Button>
                            <Button
                              variant="success"
                              size="sm"
                              onClick={() => openAddNomineeModal(category.id)}
                            >
                              Add Nominee
                            </Button>
                          </td>
                        </tr>
                        {isExpanded && categoryNominees.length > 0 && (
                          <tr>
                            <td colSpan="5" className="p-0">
                              <div className="p-3 category-expanded-section">
                                <h6 className="mb-3 category-expanded-title">Nominees in {category.name}</h6>
                                <Table size="sm" className="mb-0">
                                  <thead>
                                    <tr>
                                      <th>Name</th>
                                      <th>Description</th>
                                      <th>Actions</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {categoryNominees.map((nominee) => (
                                      <tr key={nominee.id}>
                                        <td>{nominee.name}</td>
                                        <td>{nominee.description || '-'}</td>
                                        <td>
                                          <Button
                                            variant="primary"
                                            size="sm"
                                            onClick={() => openNomineeModal(nominee)}
                                          >
                                            Edit
                                          </Button>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </Table>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </Table>
            ) : (
              <p className="text-muted">No categories found. Click "Add Category" to create one.</p>
            )}
          </Card.Body>
        </Card>

        {/* Category Edit Modal */}
        <Modal show={showCategoryModal} onHide={closeCategoryModal}>
          <Modal.Header closeButton>
            <Modal.Title>
              {editingCategory?.isNewCategory ? 'Add Category' : 'Edit Category'}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={(e) => {
              e.preventDefault();
              if (editingCategory?.isNewCategory) {
                handleCategorySubmit(e);
              } else if (editingCategory) {
                handleUpdateCategory(editingCategory.id);
              }
            }}>
              <Form.Group className="mb-3">
                <Form.Label>Category Name</Form.Label>
                <Form.Control
                  type="text"
                  value={editingCategory ? editingCategory.name : ''}
                  onChange={(e) => {
                    if (editingCategory?.isNewCategory) {
                      setEditingCategory({ ...editingCategory, name: e.target.value });
                    } else if (editingCategory) {
                      setEditingCategory({ ...editingCategory, name: e.target.value });
                    }
                  }}
                  required
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={editingCategory ? editingCategory.description : ''}
                  onChange={(e) => {
                    if (editingCategory?.isNewCategory) {
                      setEditingCategory({ ...editingCategory, description: e.target.value });
                    } else if (editingCategory) {
                      setEditingCategory({ ...editingCategory, description: e.target.value });
                    }
                  }}
                />
              </Form.Group>
              <div className="d-flex justify-content-between">
                <Button variant="secondary" onClick={closeCategoryModal}>
                  Cancel
                </Button>
                <div>
                  {!editingCategory?.isNewCategory && (
                    <Button
                      variant="danger"
                      className="me-2"
                      onClick={() => handleDeleteCategory(editingCategory.id)}
                    >
                      Delete
                    </Button>
                  )}
                  <Button type="submit" variant="primary">
                    {editingCategory?.isNewCategory ? 'Create' : 'Update'}
                  </Button>
                </div>
              </div>
            </Form>
          </Modal.Body>
        </Modal>

        {/* Nominee Edit Modal */}
        <Modal show={showNomineeModal} onHide={closeNomineeModal}>
          <Modal.Header closeButton>
            <Modal.Title>
              {editingNominee?.isNewNominee ? 'Add Nominee' : 'Edit Nominee'}
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={(e) => {
              e.preventDefault();
              if (editingNominee?.isNewNominee) {
                handleNomineeSubmit(e);
              } else if (editingNominee) {
                handleUpdateNominee(editingNominee.id);
              }
            }}>
              <Form.Group className="mb-3">
                <Form.Label>Nominee Name</Form.Label>
                <Form.Control
                  type="text"
                  value={editingNominee ? editingNominee.name : ''}
                  onChange={(e) => {
                    if (editingNominee?.isNewNominee) {
                      setEditingNominee({ ...editingNominee, name: e.target.value });
                    } else if (editingNominee) {
                      setEditingNominee({ ...editingNominee, name: e.target.value });
                    }
                  }}
                  required
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Description</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={editingNominee ? editingNominee.description : ''}
                  onChange={(e) => {
                    if (editingNominee?.isNewNominee) {
                      setEditingNominee({ ...editingNominee, description: e.target.value });
                    } else if (editingNominee) {
                      setEditingNominee({ ...editingNominee, description: e.target.value });
                    }
                  }}
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Category</Form.Label>
                <Form.Select
                  value={editingNominee?.isNewNominee ? (selectedCategoryId || '') : (editingNominee?.category_id || '')}
                  onChange={(e) => {
                    if (editingNominee?.isNewNominee) {
                      setEditingNominee({ ...editingNominee, category_id: e.target.value });
                    } else if (editingNominee) {
                      setEditingNominee({ ...editingNominee, category_id: e.target.value });
                    }
                  }}
                  required
                  disabled={!!selectedCategoryId}
                >
                  <option value="">Select a category</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </Form.Select>
                {selectedCategoryId && (
                  <Form.Text className="text-muted">
                    Category pre-selected from the table
                  </Form.Text>
                )}
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Image Source</Form.Label>
                <div className="mb-2">
                  <Form.Check
                    type="radio"
                    label="Upload Image"
                    name="imageMode"
                    id="upload-mode"
                    checked={imageInputMode === 'upload'}
                    onChange={() => setImageInputMode('upload')}
                    inline
                  />
                  <Form.Check
                    type="radio"
                    label="Image URL"
                    name="imageMode"
                    id="url-mode"
                    checked={imageInputMode === 'url'}
                    onChange={() => setImageInputMode('url')}
                    inline
                    className="ms-3"
                  />
                </div>
              </Form.Group>

              {imageInputMode === 'upload' ? (
                <Form.Group className="mb-3">
                  <Form.Label>Upload Image</Form.Label>
                  <div className="d-flex align-items-center">
                    <Form.Control
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          handleImagePreview(file);
                        }
                      }}
                      disabled={uploadingImage}
                    />
                    {uploadingImage && (
                      <Spinner animation="border" size="sm" className="ms-2" />
                    )}
                  </div>
                  {(tempImagePreview || (editingNominee?.image_url && editingNominee.image_url !== 'temp-preview')) && (
                    <div className="mt-2">
                      <img
                        src={tempImagePreview || (editingNominee.image_url.startsWith('http') ?
                          editingNominee.image_url :
                          `http://localhost:5001${editingNominee.image_url}`)}
                        alt="Preview"
                        style={{ maxWidth: '200px', maxHeight: '150px' }}
                        className="img-thumbnail"
                      />
                      <Button
                        variant="danger"
                        size="sm"
                        className="ms-2"
                        onClick={() => {
                          setTempImageFile(null);
                          setTempImagePreview('');
                          setEditingNominee(prev => ({ ...prev, image_url: '' }));
                        }}
                        title="Remove image"
                      >
                        Remove Image
                      </Button>
                    </div>
                  )}
                </Form.Group>
              ) : (
                <Form.Group className="mb-3">
                  <Form.Label>Image URL</Form.Label>
                  <Form.Control
                    type="url"
                    placeholder="https://example.com/image.jpg"
                    value={editingNominee ? editingNominee.image_url : ''}
                    onChange={(e) => {
                      if (editingNominee?.isNewNominee) {
                        setEditingNominee({ ...editingNominee, image_url: e.target.value });
                      } else if (editingNominee) {
                        setEditingNominee({ ...editingNominee, image_url: e.target.value });
                      }
                      // Clear temporary image when URL is changed
                      setTempImageFile(null);
                      setTempImagePreview('');
                    }}
                  />
                  {editingNominee?.image_url && editingNominee.image_url !== 'temp-preview' && (
                    <div className="mt-2">
                      <img
                        src={editingNominee.image_url.startsWith('http') ?
                          editingNominee.image_url :
                          `http://localhost:5001${editingNominee.image_url}`}
                        alt="Preview"
                        style={{ maxWidth: '200px', maxHeight: '150px' }}
                        className="img-thumbnail"
                      />
                    </div>
                  )}
                </Form.Group>
              )}
              <Form.Group className="mb-3">
                <Form.Label>YouTube URL (Optional)</Form.Label>
                <Form.Control
                  type="url"
                  placeholder="https://www.youtube.com/watch?v=..."
                  value={editingNominee ? editingNominee.youtube_url || '' : ''}
                  onChange={(e) => {
                    if (editingNominee?.isNewNominee) {
                      setEditingNominee({ ...editingNominee, youtube_url: e.target.value });
                    } else if (editingNominee) {
                      setEditingNominee({ ...editingNominee, youtube_url: e.target.value });
                    }
                  }}
                />
                <Form.Text className="text-muted">
                  Add a YouTube video URL for this nominee
                </Form.Text>
              </Form.Group>
              <div className="d-flex justify-content-between">
                <Button variant="secondary" onClick={closeNomineeModal}>
                  Cancel
                </Button>
                <div>
                  {!editingNominee?.isNewNominee && (
                    <Button
                      variant="danger"
                      className="me-2"
                      onClick={() => handleDeleteNominee(editingNominee.id)}
                    >
                      Delete
                    </Button>
                  )}
                  <Button type="submit" variant="primary">
                    {editingNominee?.isNewNominee ? 'Create' : 'Update'}
                  </Button>
                </div>
              </div>
            </Form>
          </Modal.Body>
        </Modal>

        {/* Password Change Modal */}
        <Modal show={showPasswordModal} onHide={closePasswordModal}>
          <Modal.Header closeButton>
            <Modal.Title>Change Password</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form onSubmit={handlePasswordChange}>
              <Form.Group className="mb-3">
                <Form.Label>Current Password</Form.Label>
                <Form.Control
                  type="password"
                  value={passwordForm.current_password}
                  onChange={(e) => setPasswordForm({...passwordForm, current_password: e.target.value})}
                  required
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>New Password</Form.Label>
                <Form.Control
                  type="password"
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                  required
                  minLength="6"
                />
                <Form.Text className="text-muted">
                  Password must be at least 6 characters long
                </Form.Text>
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Confirm New Password</Form.Label>
                <Form.Control
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                  required
                  minLength="6"
                />
              </Form.Group>
              <div className="d-flex justify-content-between">
                <Button variant="secondary" onClick={closePasswordModal}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary">
                  Change Password
                </Button>
              </div>
            </Form>
          </Modal.Body>
        </Modal>
      </div>
    </Container>
  );
};

export default Admin;

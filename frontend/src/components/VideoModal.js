import React from 'react';
import { Modal } from 'react-bootstrap';

const VideoModal = ({ show, handleClose, videoUrl, productName }) => {
  const parseTimeString = (timeStr) => {
    // Parse time strings like "1m30s", "2h15m30s", "30s", "5m", etc.
    let totalSeconds = 0;

    // Match patterns like "2h15m30s", "1m30s", "30s", "5m"
    const hourMatch = timeStr.match(/(\d+)h/);
    const minuteMatch = timeStr.match(/(\d+)m/);
    const secondMatch = timeStr.match(/(\d+)s/);

    if (hourMatch) {
      totalSeconds += parseInt(hourMatch[1]) * 3600;
    }
    if (minuteMatch) {
      totalSeconds += parseInt(minuteMatch[1]) * 60;
    }
    if (secondMatch) {
      totalSeconds += parseInt(secondMatch[1]);
    }

    return totalSeconds;
  };

  const getEmbedUrl = (url) => {
    if (!url) return '';

    // Handle different YouTube URL formats and extract timestamp
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);

    if (match && match[2].length === 11) {
      const videoId = match[2];

      // Extract timestamp from URL
      let timestamp = '';

      // Handle various timestamp formats
      const timeMatch = url.match(/[?&]t=(\d+)/);
      if (timeMatch) {
        timestamp = `&start=${timeMatch[1]}`;
      }

      // Handle timestamp in hash format (e.g., #t=1m30s, #t=2h15m30s)
      const hashMatch = url.match(/#t=([^&]+)/);
      if (hashMatch) {
        const timeStr = hashMatch[1];
        const seconds = parseTimeString(timeStr);
        timestamp = `&start=${seconds}`;
      }

      // Handle timestamp parameter in complex format (e.g., ?t=1m30s)
      const complexTimeMatch = url.match(/[?&]t=([^&]+)/);
      if (complexTimeMatch && !timestamp) {
        const timeStr = complexTimeMatch[1];
        const seconds = parseTimeString(timeStr);
        timestamp = `&start=${seconds}`;
      }

      return `https://www.youtube.com/embed/${videoId}?rel=0${timestamp}`;
    }

    return '';
  };

  const embedUrl = getEmbedUrl(videoUrl);

  return (
    <Modal
      show={show}
      onHide={handleClose}
      size="lg"
      centered
      className="video-modal"
    >
      <Modal.Header closeButton>
        <Modal.Title>{productName}</Modal.Title>
      </Modal.Header>
      <Modal.Body className="p-0">
        {embedUrl ? (
          <div className="ratio ratio-16x9">
            <iframe
              src={embedUrl}
              title={`${productName} video`}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-100"
            />
          </div>
        ) : (
          <div className="text-center p-4">
            <p>Invalid YouTube URL</p>
          </div>
        )}
      </Modal.Body>
    </Modal>
  );
};

export default VideoModal;

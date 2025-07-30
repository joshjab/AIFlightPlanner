import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ChatInterface from './ChatInterface';

describe('ChatInterface', () => {
  it('renders in collapsed state with waiting message when not enabled', () => {
    render(<ChatInterface enabled={false} />);
    expect(screen.getByText(/Waiting for acknowledgement/i)).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeDisabled();
    expect(screen.getByRole('button', { name: /Send/i })).toBeDisabled();
    expect(screen.getByPlaceholderText(/Acknowledge briefing to chat/i)).toBeInTheDocument();
  });

  it('renders in expanded state with welcome message when enabled', () => {
    render(<ChatInterface enabled={true} />);
    expect(screen.getByText(/Welcome! How can I help you/i)).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeEnabled();
    expect(screen.getByRole('button', { name: /Send/i })).toBeEnabled();
    expect(screen.getByPlaceholderText(/Type your message/i)).toBeInTheDocument();
  });
});

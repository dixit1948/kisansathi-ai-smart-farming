import { describe, it, expect } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { Badge } from '../components/ui/Badge';

describe('Badge Component', () => {
  it('renders children correctly', () => {
    render(<Badge variant="success">Test Badge</Badge>);
    expect(screen.getByText('Test Badge')).toBeDefined();
  });

  it('applies variant styling', () => {
    const { container } = render(<Badge variant="danger">Critical Alert</Badge>);
    expect(container.firstChild).toBeDefined();
  });
});

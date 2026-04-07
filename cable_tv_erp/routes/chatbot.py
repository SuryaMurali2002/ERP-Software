"""
routes/chatbot.py — Flask route for the ERP Assistant chatbot UI and API endpoint.
"""

import logging
import sys
import os

from flask import Blueprint, render_template, request, jsonify, session
from routes.auth import login_required_session

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/chatbot')
@login_required_session
def index():
    """Render the chatbot UI."""
    return render_template('chatbot/index.html')


@chatbot_bp.route('/chatbot/ask', methods=['POST'])
@login_required_session
def ask():
    """
    JSON API endpoint for the chatbot.

    Accepts:  { "query": "...", "top_k": 5 }
    Returns:  { "answer": "...", "sources": [...], "query": "..." }
    On error: { "error": "..." }  with HTTP 500
    """
    try:
        data  = request.get_json(silent=True) or {}
        query = (data.get('query') or '').strip()
        top_k = int(data.get('top_k', 5))

        if not query:
            return jsonify({'error': 'Query is required.'}), 400

        # Clamp top_k to a sensible range
        top_k = max(1, min(top_k, 20))

        # Import here so Flask starts even if the index hasn't been built yet
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from rag.generator import rag_query

        result = rag_query(query, top_k=top_k)

        sources = [
            {
                'id':      doc['id'],
                'table':   doc['metadata'].get('table', 'unknown'),
                'preview': doc['text'][:100].replace('\n', ' ')
            }
            for doc in result.get('retrieved_docs', [])
        ]

        return jsonify({
            'query':   result['query'],
            'answer':  result['answer'],
            'sources': sources,
        })

    except RuntimeError as e:
        # ChromaDB index not built yet
        msg = str(e)
        logging.warning(f"Chatbot RuntimeError: {msg}")
        return jsonify({'error': msg}), 503

    except ValueError as e:
        # No OpenAI API key
        msg = str(e)
        logging.warning(f"Chatbot ValueError: {msg}")
        return jsonify({'error': msg}), 503

    except Exception as e:
        logging.error(f"Chatbot error: {e}", exc_info=True)
        return jsonify({'error': 'Something went wrong. Please try again.'}), 500

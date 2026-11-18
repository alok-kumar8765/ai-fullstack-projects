import React, { useEffect, useRef, useState } from 'react';
import * as fabric from 'fabric'; // Fabric v6+ syntax

const API_BASE = 'http://localhost:8000';

export default function CartoonCreator() {
  const canvasRef = useRef(null);
  const [fabricCanvas, setFabricCanvas] = useState(null);
  const [savedUrl, setSavedUrl] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  // Initialize Canvas
  useEffect(() => {
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 600,
      height: 450,
      backgroundColor: '#87CEEB',
      preserveObjectStacking: true, // Prevents selected items from jumping to top automatically
    });

    setFabricCanvas(canvas);
    return () => canvas.dispose();
  }, []);

  // Add Character / Asset to Canvas
  const addCharacter = async (imageUrl) => {
    if (!fabricCanvas) return;
    try {
      const img = await fabric.FabricImage.fromURL(imageUrl, { crossOrigin: 'anonymous' });
      img.scaleToWidth(180);
      img.set({ left: 150, top: 100 });
      fabricCanvas.add(img);
      fabricCanvas.setActiveObject(img);
      fabricCanvas.renderAll();
    } catch (err) {
      console.error('Error loading asset:', err);
    }
  };

  // Add Editable Speech Text
  const addText = () => {
    if (!fabricCanvas) return;
    const text = new fabric.IText('Hey there!', {
      left: 320,
      top: 80,
      fontFamily: 'Comic Sans MS, sans-serif',
      fontSize: 24,
      fill: '#111111',
      fontWeight: 'bold',
    });
    fabricCanvas.add(text);
    fabricCanvas.setActiveObject(text);
  };

  // Layer Controls (Z-Index)
  const changeLayer = (direction) => {
    if (!fabricCanvas) return;
    const activeObj = fabricCanvas.getActiveObject();
    if (!activeObj) return;

    if (direction === 'up') fabricCanvas.bringObjectForward(activeObj);
    if (direction === 'down') fabricCanvas.sendObjectBackwards(activeObj);
    fabricCanvas.renderAll();
  };

  // Delete Selected Object
  const deleteSelected = () => {
    if (!fabricCanvas) return;
    const activeObj = fabricCanvas.getActiveObject();
    if (activeObj) {
      fabricCanvas.remove(activeObj);
      fabricCanvas.discardActiveObject();
      fabricCanvas.renderAll();
    }
  };

  // Save State & High-Res Export to Python Backend
  const handleSave = async () => {
    if (!fabricCanvas) return;
    setIsSaving(true);
    try {
      const dataURL = fabricCanvas.toDataURL({ format: 'png', multiplier: 2 }); // 2x Retina export
      const canvasJSON = fabricCanvas.toJSON();

      const res = await fetch(`${API_BASE}/api/cartoons/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: 'My Cartoon Creation',
          canvas_json: canvasJSON,
          image_base64: dataURL,
        }),
      });

      const data = await res.json();
      setSavedUrl(data.image_url);
    } catch (err) {
      console.error('Save failed:', err);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div style={{ maxWidth: '700px', margin: '0 auto', fontFamily: 'sans-serif' }}>
      <h2>Cartoon Studio</h2>

      {/* Toolbar */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        <button onClick={() => addCharacter('/assets/boy_casual.png')}>+ Add Boy</button>
        <button onClick={() => addCharacter('/assets/girl_hoodie.png')}>+ Add Girl</button>
        <button onClick={addText}>+ Add Text</button>
        <button onClick={() => changeLayer('up')}>Bring Forward</button>
        <button onClick={() => changeLayer('down')}>Send Backward</button>
        <button onClick={deleteSelected} style={{ color: 'red' }}>Delete Selected</button>
      </div>

      {/* Interactive Canvas */}
      <div style={{ border: '2px solid #333', display: 'inline-block' }}>
        <canvas ref={canvasRef} />
      </div>

      {/* Action Bar */}
      <div style={{ marginTop: '16px' }}>
        <button 
          onClick={handleSave} 
          disabled={isSaving}
          style={{ padding: '10px 20px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '6px' }}
        >
          {isSaving ? 'Exporting...' : 'Save & Export Cartoon'}
        </button>
      </div>

      {savedUrl && (
        <div style={{ marginTop: '16px', padding: '12px', background: '#ecfdf5', borderRadius: '6px' }}>
          <strong>Saved!</strong> View high-res export: <a href={savedUrl} target="_blank" rel="noreferrer">{savedUrl}</a>
        </div>
      )}
    </div>
  );
}
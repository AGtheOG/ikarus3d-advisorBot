# Ikarus3D Advisor Bot

A smart, interactive assistant designed to help users explore available products through an intuitive chat interface.

---

## 🏠 Landing Page
The landing page introduces users to the Advisor Bot with a sleek UI and quick navigation options.  
It highlights the core features and helps users get started instantly.  
![Landing Page](./assets/landing%20page.png)

---

## 📊 Analytics Page
The analytics dashboard displays key metrics and visual summaries of available products.  
It helps monitor trends and track actionable insights easily.  
![Analytics Page](./assets/analytics%20page.png)

---

## 💬 Reco system demo
This screen demonstrates the chat interaction with the Advisor Bot where user can get custom recommndations for their required product.

![Demo 01](./assets/demo01.png)

![Demo 02](./assets/demo02.png)

![Demo 03](./assets/demo03.png)

### 📸 Assets
All screenshots are stored in the `/assets` directory.


---

## 🧩 Recommendation System

### 🔹 Version 1 — Hybrid Embeddings
- Combined **text embeddings** (product descriptions) with **image embeddings** (CNN features).  
- Used cosine similarity for retrieval.  
- Faced reduced accuracy due to inconsistent feature scaling and cross-modal variance.
- recoSystem1.ipynb and backend
- 
### 🔹 Version 2 — CLIP ViT-B/32 Model
- Switched to **CLIP (ViT-B/32)** for unified text–image embedding space.  
- Achieved significantly better retrieval accuracy and faster inference.  
- Integrated into the second backend version (`model_v2`).
- recoSystem2.ipynb and backendv1
---

## 🪣 Vector Storage with Pinecone
- All image and text embeddings are stored and indexed in **Pinecone** for efficient similarity search.  
- Enables real-time retrieval for recommendations and analytics queries.

---

## 🚀 Tech Stack
- **Frontend:** React + Tailwind CSS  
- **Backend:** FastAPI  
- **AI / ML:** CLIP (ViT-B/32), Hybrid Embeddings  
- **Vector DB:** Pinecone 
- **Visualization:** Matplotlib, Plotly

---

## 📈 Future Improvements
- Fine-tuning CLIP embeddings on domain-specific data  
- Incorporating user interaction feedback loops  
- Extending analytics to include session-based recommendations







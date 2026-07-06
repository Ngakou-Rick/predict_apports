'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Upload, Activity, TrendingUp, Download, Check, AlertCircle } from 'lucide-react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [season, setSeason] = useState<string>('dry');
  const [availableYears, setAvailableYears] = useState<string[]>([]);
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [model, setModel] = useState<string>('random_forest');

  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);

  const API_URL = 'http://localhost:8000/api';

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setUploadStatus('Uploading...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus('Upload successful!');
      fetchYears(season);
    } catch (error) {
      console.error(error);
      setUploadStatus('Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const fetchYears = async (seasonType: string) => {
    try {
      const response = await axios.get(`${API_URL}/years/${seasonType}`);
      setAvailableYears(response.data.years);
      if (response.data.years.length > 0) {
        setSelectedYear(response.data.years[0]);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleSeasonChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const s = e.target.value;
    setSeason(s);
    if (uploadStatus === 'Upload successful!') {
      fetchYears(s);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedYear) return;
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/analyze`, {
        params: { season_type: season, year: selectedYear }
      });
      setAnalysisResult(response.data.results);
      setPredictionResult(null); // Clear previous predictions
    } catch (error) {
      console.error(error);
      alert('Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedYear) return;
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/predict`, null, {
        params: { season_type: season, year: selectedYear, model_name: model }
      });
      setPredictionResult(response.data);
    } catch (error) {
      console.error(error);
      alert('Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  // Format prediction data for Recharts
  const formatChartData = () => {
    if (!predictionResult || !predictionResult.chart_data) return [];

    const data = [];
    const { dates, actual, predicted } = predictionResult.chart_data;

    for (let i = 0; i < dates.length; i++) {
      data.push({
        date: dates[i],
        actual: actual[i],
        predicted: predicted[i]
      });
    }
    return data;
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-blue-900 mb-2">🌊 Prévision Hydrologique</h1>
          <p className="text-gray-600 text-lg">Barrage de Mbakaou - Système d'Analyse et de Prédiction</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          {/* Sidebar - Controls */}
          <div className="bg-white p-6 rounded-xl shadow-md flex flex-col gap-6">

            {/* Upload Section */}
            <div className="border border-gray-200 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Upload size={20} /> 1. Chargement des données
              </h2>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 mb-4 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <button
                onClick={handleUpload}
                disabled={!file || loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-md transition disabled:opacity-50"
              >
                {loading ? 'Chargement...' : 'Charger'}
              </button>
              {uploadStatus && (
                <p className={`mt-2 text-sm flex items-center gap-1 ${uploadStatus.includes('success') ? 'text-green-600' : 'text-red-600'}`}>
                  {uploadStatus.includes('success') ? <Check size={16} /> : <AlertCircle size={16} />}
                  {uploadStatus}
                </p>
              )}
            </div>

            {/* Selection Section */}
            <div className="border border-gray-200 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Activity size={20} /> 2. Paramètres
              </h2>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Saison</label>
                <select
                  value={season}
                  onChange={handleSeasonChange}
                  className="w-full border border-gray-300 rounded-md p-2"
                  disabled={!availableYears.length}
                >
                  <option value="dry">Saison Sèche (Déc-Mai)</option>
                  <option value="rainy">Saison des Pluies (Juin-Nov)</option>
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Année Hydrologique</label>
                <select
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                  disabled={!availableYears.length}
                >
                  {availableYears.map(year => (
                    <option key={year} value={year}>{year}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={!selectedYear || loading}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-md transition disabled:opacity-50"
              >
                Analyser
              </button>
            </div>

            {/* Prediction Section */}
            <div className="border border-gray-200 p-4 rounded-lg">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <TrendingUp size={20} /> 3. Prédiction
              </h2>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-1">Modèle</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full border border-gray-300 rounded-md p-2"
                  disabled={!availableYears.length}
                >
                  <option value="random_forest">Random Forest</option>
                  <option value="xgboost">XGBoost</option>
                  <option value="linear_regression">Régression Linéaire</option>
                </select>
              </div>

              <button
                onClick={handlePredict}
                disabled={!selectedYear || loading}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white py-2 rounded-md transition disabled:opacity-50"
              >
                Prédire
              </button>
            </div>

          </div>

          {/* Main Content Area */}
          <div className="md:col-span-2 flex flex-col gap-8">

            {/* Analysis Results */}
            {analysisResult && !predictionResult && (
              <div className="bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold mb-4 border-b pb-2">Résultats de l'Analyse</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded border">
                    <p className="text-sm text-gray-500">Moyenne</p>
                    <p className="text-2xl font-bold">{analysisResult.stats?.mean?.toFixed(2) || '-'} m³/s</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded border">
                    <p className="text-sm text-gray-500">Maximum</p>
                    <p className="text-2xl font-bold">{analysisResult.stats?.max?.toFixed(2) || '-'} m³/s</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded border">
                    <p className="text-sm text-gray-500">Minimum</p>
                    <p className="text-2xl font-bold">{analysisResult.stats?.min?.toFixed(2) || '-'} m³/s</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded border">
                    <p className="text-sm text-gray-500">Coefficient de variation</p>
                    <p className="text-2xl font-bold">{analysisResult.stats?.cv?.toFixed(2) || '-'} %</p>
                  </div>
                </div>
              </div>
            )}

            {/* Prediction Results */}
            {predictionResult && (
              <div className="bg-white p-6 rounded-xl shadow-md">
                <h3 className="text-xl font-semibold mb-4 border-b pb-2 flex justify-between items-center">
                  <span>Résultats de la Prédiction ({model})</span>
                  <div className="flex gap-4 text-sm font-normal">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                      R²: {predictionResult.metrics?.test?.r2?.toFixed(3)}
                    </span>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      RMSE: {predictionResult.metrics?.test?.rmse?.toFixed(2)}
                    </span>
                  </div>
                </h3>

                <div className="h-80 w-full mt-6">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={formatChartData()}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="date" tick={{fontSize: 12}} />
                      <YAxis domain={['auto', 'auto']} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="actual" stroke="#8884d8" name="Débit Réel" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="predicted" stroke="#82ca9d" name="Débit Prédit" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Placeholder state */}
            {!analysisResult && !predictionResult && (
              <div className="bg-white p-6 rounded-xl shadow-md h-full flex items-center justify-center text-gray-400 min-h-[400px]">
                <div className="text-center">
                  <Activity size={48} className="mx-auto mb-4 opacity-50" />
                  <p>Chargez un fichier et lancez une analyse pour voir les résultats ici.</p>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

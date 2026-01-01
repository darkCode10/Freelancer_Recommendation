# 🔗 App Integration Guide

How to integrate the recommendation system into your mobile/web app.

---

## ⚡ **Quick Answer: Add Freelancer Before 2 AM?**

**Q:** I add a freelancer at 1 AM. Will the system train?

**A:** You have 2 options:

### Option 1: Wait for Cron (Automatic)
- ⏰ Cron runs at 2 AM
- ⏳ New freelancer searchable after 2 AM
- ❌ 1 hour delay

### Option 2: Trigger `/retrain` (Recommended)
- 🚀 Call endpoint immediately
- ⚡ New freelancer searchable in 10-30 seconds
- ✅ Best user experience

---

## 📱 **Mobile/Web App Integration**

### **1. Add Freelancer & Update Model**

```javascript
// React/React Native Example
async function addFreelancer(freelancerData) {
  try {
    // Step 1: Add to Supabase
    const { data, error } = await supabase
      .from('freelancers')
      .insert({
        username: freelancerData.username,
        skills: freelancerData.skills,  // Array: ['Python', 'AWS']
        experience: freelancerData.experience
      });
    
    if (error) throw error;
    
    // Step 2: Update recommendation model (optional but recommended)
    const retrainResponse = await fetch(
      'https://your-app.railway.app/retrain',
      { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      }
    );
    
    const retrainData = await retrainResponse.json();
    
    if (retrainData.success) {
      console.log(`✅ Model updated with ${retrainData.freelancers_count} freelancers`);
      return { 
        success: true, 
        message: 'Freelancer added and immediately searchable!' 
      };
    } else {
      // Retrain failed, but freelancer is added
      // Will be searchable after cron job at 2 AM
      return { 
        success: true, 
        message: 'Freelancer added (searchable after 2 AM)' 
      };
    }
    
  } catch (error) {
    console.error('Error:', error);
    return { success: false, error: error.message };
  }
}

// Usage
const result = await addFreelancer({
  username: 'John Doe',
  skills: ['Python', 'Machine Learning', 'AWS'],
  experience: 5
});

if (result.success) {
  alert(result.message);
}
```

---

### **2. Search for Freelancers**

```javascript
async function searchFreelancers(skills, topN = 5) {
  try {
    const response = await fetch(
      'https://your-app.railway.app/recommend',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skills: skills,  // ['Python', 'Django']
          top_n: topN
        })
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      return {
        success: true,
        freelancers: data.recommendations
      };
    } else {
      return {
        success: false,
        message: data.message || 'No matching freelancers found'
      };
    }
    
  } catch (error) {
    console.error('Error:', error);
    return { success: false, error: error.message };
  }
}

// Usage
const result = await searchFreelancers(['Python', 'Machine Learning'], 5);

if (result.success) {
  result.freelancers.forEach(freelancer => {
    console.log(`${freelancer.name} - ${freelancer.match}% match`);
  });
} else {
  console.log(result.message);
}
```

---

### **3. Admin Panel - Manual Model Update**

```javascript
// React Component Example
function AdminPanel() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  
  const handleRetrain = async () => {
    setLoading(true);
    setStatus('Updating model...');
    
    try {
      const response = await fetch(
        'https://your-app.railway.app/retrain',
        { method: 'POST' }
      );
      
      const data = await response.json();
      
      if (data.success) {
        setStatus(
          `✅ Model updated! ${data.freelancers_count} freelancers, ` +
          `${data.vocabulary_size} skills learned`
        );
      } else {
        setStatus('❌ Update failed. Will auto-update at 2 AM.');
      }
    } catch (error) {
      setStatus('❌ Error: ' + error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <h2>Admin Panel</h2>
      <button onClick={handleRetrain} disabled={loading}>
        {loading ? 'Updating...' : '🔄 Update Recommendation Model'}
      </button>
      <p>{status}</p>
    </div>
  );
}
```

---

### **4. React Native Example**

```javascript
import { supabase } from './supabaseClient';

// Add Freelancer Screen
const AddFreelancerScreen = () => {
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (formData) => {
    setLoading(true);
    
    try {
      // 1. Add to Supabase
      const { data, error } = await supabase
        .from('freelancers')
        .insert({
          username: formData.username,
          skills: formData.skills,
          experience: parseInt(formData.experience)
        });
      
      if (error) throw error;
      
      Alert.alert('Success', 'Freelancer added to database');
      
      // 2. Update model (background - don't wait)
      fetch('https://your-app.railway.app/retrain', { 
        method: 'POST' 
      })
      .then(() => console.log('Model updated'))
      .catch(() => console.log('Will update at 2 AM'));
      
      navigation.goBack();
      
    } catch (error) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <View>
      {/* Form fields */}
      <Button 
        title={loading ? 'Adding...' : 'Add Freelancer'} 
        onPress={handleSubmit}
        disabled={loading}
      />
    </View>
  );
};
```

---

## 🎯 **Best Practices**

### **1. When to Call `/retrain`**

✅ **Good times:**
- After adding new freelancer
- After bulk import
- When admin manually triggers
- Once or twice per day maximum

❌ **Bad times:**
- After every single action
- More than once per minute
- In a loop

### **2. Error Handling**

```javascript
// Handle retrain failures gracefully
async function safeRetrain() {
  try {
    const response = await fetch(
      'https://your-app.railway.app/retrain',
      { 
        method: 'POST',
        timeout: 60000  // 60 second timeout
      }
    );
    
    if (!response.ok) throw new Error('Retrain failed');
    
    return await response.json();
  } catch (error) {
    // Don't fail the entire operation if retrain fails
    console.warn('Model update failed, will retry at 2 AM:', error);
    return { success: false };
  }
}
```

### **3. Loading States**

```javascript
// Show user-friendly loading state
async function addWithFeedback(data) {
  showLoading('Adding freelancer...');
  
  // Add to database
  await supabase.from('freelancers').insert(data);
  
  showLoading('Updating search index...');
  
  // Update model (optional)
  await fetch('https://your-app.railway.app/retrain', { 
    method: 'POST' 
  });
  
  hideLoading();
  showSuccess('Freelancer added and searchable!');
}
```

---

## 📊 **Architecture**

```
Your App                    Railway API              Supabase
--------                    -----------              --------
  |                              |                       |
  |-- 1. Add Freelancer -------->|---------------------->|
  |                              |                       |
  |-- 2. Call /retrain --------->|                       |
  |                              |-- Fetch Data -------->|
  |                              |<-- Return Data -------|
  |                              |-- Train Model         |
  |<-- Success ------------------|                       |
  |                              |                       |
  |-- 3. Search /recommend ----->|                       |
  |                              |-- Fetch Data -------->|
  |                              |-- Calculate Match     |
  |<-- Results ------------------|                       |
```

---

## 🔄 **Update Frequency**

| Method | Frequency | Use Case |
|--------|-----------|----------|
| **Cron Job** | Daily (2 AM) | Background maintenance |
| **Manual `/retrain`** | On-demand | After adding freelancers |
| **Auto in App** | After add | Best UX |

---

## ✅ **Complete Example**

```javascript
// Complete freelancer management module
class FreelancerService {
  constructor(apiUrl) {
    this.apiUrl = apiUrl;
  }
  
  async add(freelancerData) {
    // Add to Supabase
    const { data, error } = await supabase
      .from('freelancers')
      .insert(freelancerData);
    
    if (error) throw error;
    
    // Update model (non-blocking)
    this.updateModel().catch(console.warn);
    
    return data;
  }
  
  async search(skills, topN = 5) {
    const response = await fetch(`${this.apiUrl}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ skills, top_n: topN })
    });
    
    return await response.json();
  }
  
  async updateModel() {
    const response = await fetch(`${this.apiUrl}/retrain`, {
      method: 'POST'
    });
    
    return await response.json();
  }
}

// Usage
const service = new FreelancerService('https://your-app.railway.app');

// Add freelancer
await service.add({
  username: 'John Doe',
  skills: ['Python', 'AWS'],
  experience: 5
});

// Search
const results = await service.search(['Python', 'Machine Learning']);
console.log(results.recommendations);

// Manual model update (admin only)
await service.updateModel();
```

---

## 🚀 **Summary**

**Q: Add freelancer before 2 AM - will system train?**

**A:** Use this pattern:

```javascript
// 1. Add freelancer
await supabase.from('freelancers').insert(data);

// 2. Trigger immediate update (optional)
await fetch('https://your-app.railway.app/retrain', { 
  method: 'POST' 
});

// 3. New freelancer is searchable in 10-30 seconds!
```

**No need to wait for 2 AM!** ⚡


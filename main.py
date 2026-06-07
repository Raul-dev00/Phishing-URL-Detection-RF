import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

# 1. Veriyi Yükleme
# Dosya adının IDE'nde 'Dataset.csv' (büyük D ile) olduğunu görüyorum.
df = pd.read_csv("Dataset.csv")

# 2. Veri Ön İşleme
hedef_sutun = 'label'

# Metin (string) içeren sütunları eğitimden çıkarıyoruz.
# Geriye kalan _len, _cnt ve _ratio gibi sayısal sütunlar modelde kullanılacak.
X = df.drop(columns=['url', 'dom', 'tld', hedef_sutun])
y = df[hedef_sutun]

# Veriyi Eğitim (%80) ve Test (%20) olarak ayırma
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Model Eğitimi
# n_jobs=-1 parametresi eğitimi hızlandırır
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf_model.fit(X_train, y_train)

# Test seti üzerinde tahmin yapma
y_pred = rf_model.predict(X_test)

# 4. Performans Ölçütlerinin Hesaplanması
cm = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

accuracy = accuracy_score(y_test, y_pred)
sensitivity = tp / (tp + fn)
specificity = tn / (tn + fp)
f_measure = f1_score(y_test, y_pred)

print("-" * 34)
print(f"--- Model Performans Sonuçları ---")
print(f"Accuracy (Doğruluk):  {accuracy:.4f}")
print(f"Sensitivity (Duyarlılık): {sensitivity:.4f}")
print(f"Specificity (Özgüllük): {specificity:.4f}")
print(f"F-measure (F1-Skoru): {f_measure:.4f}")
print("-" * 34)

# 5. Görselleştirmeler (Rapor İçin)
# confusion
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=['Zararsız (0)', 'Phishing (1)'],
            yticklabels=['Zararsız (0)', 'Phishing (1)'])
plt.title("Random Forest - Karmaşıklık Matrisi")
plt.xlabel("Tahmin Edilen Etiket")
plt.ylabel("Gerçek Etiket")
plt.tight_layout()
plt.savefig('confusion_matrix.png', bbox_inches='tight')
plt.close()

# Şekil 2: Özellik Önemi (Feature Importance)
feature_importances = pd.Series(rf_model.feature_importances_, index=X.columns)
top_features = feature_importances.nlargest(10)

plt.figure(figsize=(10, 6))
top_features.plot(kind='barh', color='teal')
plt.title("En Önemli 10 Özellik (Feature Importance)")
plt.xlabel("Önem Skoru")
plt.ylabel("Özellikler")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('feature_importance.png', bbox_inches='tight')
plt.close()

from sklearn.metrics import roc_curve, auc

# Modelin tahmin olasılıklarını hesaplama (Sadece '1' yani Phishing sınıfı için)
y_pred_proba = rf_model.predict_proba(X_test)[:, 1]

# False Positive Rate (FPR) ve True Positive Rate (TPR) değerlerini alma
fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)

# AUC (Eğri Altında Kalan Alan) skorunu hesaplama
roc_auc = auc(fpr, tpr)

print(f"AUC Skoru: {roc_auc:.4f}")

# Şekil 3: ROC Eğrisi
# (Bu kısmın çalışması için kodun üst kısımlarında y_pred_proba, fpr, tpr ve roc_auc tanımlanmış olmalıdır)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC Eğrisi (AUC = {roc_auc:.4f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (Yanlış Pozitif Oranı)')
plt.ylabel('True Positive Rate (Doğru Pozitif Oranı)')
plt.title('Random Forest - ROC Eğrisi')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig('roc_curve.png', bbox_inches='tight')
plt.close()

print("Confusion Matrix, Feature Importance ve ROC Eğrisi başarıyla kaydedildi!")

from sklearn.metrics import precision_recall_curve
from sklearn.tree import plot_tree

print("Ekstra grafikler oluşturuluyor ve kaydediliyor...")

# 1. Sınıf Dağılımı (Class Distribution)
plt.figure(figsize=(6, 4))
sns.countplot(x=y, palette='Set2')
plt.title('Sınıf Dağılımı (0: Zararsız, 1: Phishing)')
plt.xlabel('Sınıf (Label)')
plt.ylabel('Frekans')
plt.savefig('sinif_dagilimi.png', bbox_inches='tight')
plt.close()

# 2. Korelasyon Matrisi (Correlation Matrix)
plt.figure(figsize=(16, 12))
# Sadece sayısal sütunların korelasyonunu alıyoruz
corr_matrix = X.corr()
sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', linewidths=0.5)
plt.title('Özellikler Arası Korelasyon Matrisi')
plt.savefig('korelasyon_matrisi.png', bbox_inches='tight')
plt.close()

# 3. Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
plt.figure(figsize=(8, 6))
plt.plot(recall, precision, color='purple', lw=2)
plt.xlabel('Recall (Duyarlılık)')
plt.ylabel('Precision (Kesinlik)')
plt.title('Precision-Recall Eğrisi')
plt.savefig('precision_recall_curve.png', bbox_inches='tight')
plt.close()

# 4. Metrikler Çubuk Grafiği
plt.figure(figsize=(8, 6))
metrik_isimleri = ['Accuracy', 'Sensitivity', 'Specificity', 'F-Measure']
metrik_degerleri = [accuracy, sensitivity, specificity, f_measure]
sns.barplot(x=metrik_isimleri, y=metrik_degerleri, palette='viridis')
plt.ylim(0, 1.1)
plt.title('Model Değerlendirme Metrikleri')
for i, v in enumerate(metrik_degerleri):
    plt.text(i, v + 0.02, f"{v:.4f}", ha='center', fontweight='bold')
plt.savefig('metrikler.png', bbox_inches='tight')
plt.close()

# 5. Örnek Bir Karar Ağacı Görselleştirmesi (Forest içindeki ilk ağaç)
plt.figure(figsize=(20, 10))
# Ağacın çok karmaşık görünmemesi için max_depth=3 veriyoruz
plot_tree(rf_model.estimators_[0], feature_names=X.columns, class_names=['Zararsız', 'Phishing'], filled=True, rounded=True, max_depth=3)
plt.title('Random Forest İçinden Örnek Bir Karar Ağacı (Derinlik Sınırlandırılmış)')
plt.savefig('decision_tree.png', bbox_inches='tight')
plt.close()

print("Tüm grafikler başarıyla kaydedildi!")
<template>
  <v-container class="d-flex justify-center align-center">
    <!-- Card for the form -->
    <v-card class="elevation-3 pa-5 rounded-lg" max-width="500">
      <!-- Header with new color and layout -->
      <v-card-title class="bg-primary text-white rounded-t-lg">
        <v-toolbar flat dense>
          <v-toolbar-title class="font-weight-bold">ตั้งเวลา</v-toolbar-title>
        </v-toolbar>
      </v-card-title>

      <!-- Form inside card with more spacing -->
      <v-form ref="form" class="mt-4" @submit.prevent="submitTime">
        <!-- Time start input with custom design -->
        <v-text-field
          v-model="time_start"
          label="เวลาเริ่มต้น"
          type="datetime-local"
          required
          :rules="[rules.required]"
          outlined
          dense
          color="primary"
        ></v-text-field>

        <!-- Time end input with custom design -->
        <v-text-field
          v-model="time_end"
          label="เวลาสิ้นสุด"
          type="datetime-local"
          required
          :rules="[rules.required]"
          outlined
          dense
          color="primary"
        ></v-text-field>

        <!-- Submit button with gradient effect and margin -->
        <v-btn block class="mt-4" color="primary" type="submit" elevation="2">
          ยืนยันการบันทึก
        </v-btn>
      </v-form>
    </v-card>

    <!-- Snackbar for notifications with custom design -->
    <v-snackbar v-model="notification" :color="notificationColor" timeout="3000">
      {{ notificationMessage }}
      <v-btn text @click="notification = false" class="text-white">ปิด</v-btn>
    </v-snackbar>
  </v-container>
</template>

<style scoped>
/* Custom styles for softer and more modern look */
.v-card {
  border-radius: 12px;
  background-color: #f9f9f9;
}

.v-card-title {
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}

.v-btn {
  background: linear-gradient(45deg, #42a5f5, #1e88e5);
  color: white;
}

.v-text-field {
  margin-bottom: 20px;
}

.v-snackbar {
  border-radius: 8px;
}

.v-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>

<script>
import axios from 'axios';

export default {
  data: () => ({
    time_start: '',
    time_end: '',
    notification: false,
    notificationColor: 'success',
    notificationMessage: '',
    rules: {
      required: value => !!value || 'กรุณากรอกข้อมูลให้ครบถ้วน',
    },
  }),

  methods: {
    async submitTime() {
      const form = this.$refs.form;

      // ตรวจสอบฟอร์ม
      if (!form.validate()) {
        this.notificationColor = 'error';
        this.notificationMessage = 'โปรดกรอกข้อมูลให้ครบ';
        this.notification = true;
        return;
      }

      try {
        await axios.post('http://localhost:9999/set-time', {
          start_time: this.time_start,
          end_time: this.time_end,
        });
        this.notificationColor = 'success';
        this.notificationMessage = 'บันทึกข้อมูลสำเร็จ';
        this.notification = true;

        setTimeout(() => {
          this.$router.push('project_f');
        }, 2000);
      } catch (error) {
        console.error('Error:', error);
        this.notificationColor = 'error';
        this.notificationMessage = 'เกิดข้อผิดพลาดในการบันทึกข้อมูล';
        this.notification = true;
      }
    },
  },
};
</script>


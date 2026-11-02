"""
Pruebas Unitarias del Sistema Clínico Fisioterapia Kalesi
Total: 40 pruebas unitarias (PU-001 a PU-040) distribuidas en 8 módulos.
Diseñadas para ejecutarse con pytest o coverage:
    coverage run manage.py test test_units
    coverage report
"""

from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

# Modelos del sistema
from users.models import CustomUser, DocumentType
from paciente.models import Patient
from expedientes.models import (
    Expediente,
    PrimeraConsulta,
    ConsultaSegumiento,
    BaseEvaluacionDolor
)
from citas.models import Cita
from cuestionarios.models import (
    Cuestionario,
    PreguntaCuestionario,
    RespuestaCuestionario,
    AnalisisPredictivoEscala,
    EvolucionPaciente
)
from cuestionarios.services import AnalisisPredictivoService
from core.services import calcular_edad, es_mayor_edad, es_menor_edad


# ==============================================================================
# 1. MÓDULO DE USUARIOS — PU-001 a PU-005
# ==============================================================================
class ModuloUsuariosTests(TestCase):
    """Pruebas unitarias para la gestión y validación de usuarios"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )

    def test_crear_usuario_valido(self):
        """PU-001: Verifica la creación correcta de un usuario."""
        user = CustomUser.objects.create_user(
            username='terapeuta_juan',
            email='juan@kalesi.com',
            password='Password123!',
            first_name='Juan',
            last_name='Perez',
            tipo_usuario='FISIO',
            document_number='10203040',
            document_type=self.doc_type
        )
        self.assertIsNotNone(user.pk)
        self.assertEqual(user.username, 'terapeuta_juan')
        self.assertEqual(user.email, 'juan@kalesi.com')
        self.assertTrue(user.is_active)

    def test_email_unico(self):
        """PU-002: Verifica que no se permitan correos duplicados."""
        CustomUser.objects.create_user(
            username='user_a',
            email='duplicado@kalesi.com',
            password='Password123!',
            tipo_usuario='RECEP',
            document_number='DOC-001',
            document_type=self.doc_type
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='user_b',
                email='duplicado@kalesi.com',
                password='Password123!',
                tipo_usuario='RECEP',
                document_number='DOC-002',
                document_type=self.doc_type
            )

    def test_documento_unico(self):
        """PU-003: Verifica la unicidad del documento de identidad."""
        CustomUser.objects.create_user(
            username='doc_user_1',
            email='doc1@kalesi.com',
            password='Password123!',
            tipo_usuario='MEDIC',
            document_number='CI-998877',
            document_type=self.doc_type
        )
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='doc_user_2',
                email='doc2@kalesi.com',
                password='Password123!',
                tipo_usuario='MEDIC',
                document_number='CI-998877',
                document_type=self.doc_type
            )

    def test_campos_obligatorios_usuario(self):
        """PU-004: Verifica los datos obligatorios del usuario."""
        user = CustomUser(
            username='',
            email='sin_username@kalesi.com',
            tipo_usuario='ADMIN',
            document_number='DOC-REQ-01'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_tipo_usuario(self):
        """PU-005: Verifica la asignación y propiedades del tipo de usuario."""
        admin = CustomUser.objects.create_user(
            username='admin_u',
            email='admin@kalesi.com',
            password='pass',
            tipo_usuario='ADMIN',
            document_number='DOC-ADM'
        )
        medico = CustomUser.objects.create_user(
            username='medico_u',
            email='medico@kalesi.com',
            password='pass',
            tipo_usuario='MEDIC',
            document_number='DOC-MED'
        )
        fisio = CustomUser.objects.create_user(
            username='fisio_u',
            email='fisio@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='DOC-FIS'
        )
        recep = CustomUser.objects.create_user(
            username='recep_u',
            email='recep@kalesi.com',
            password='pass',
            tipo_usuario='RECEP',
            document_number='DOC-REC'
        )

        self.assertTrue(medico.is_medico)
        self.assertTrue(fisio.is_fisio)
        self.assertTrue(recep.is_recepcionista)
        self.assertEqual(admin.get_tipo_usuario_display(), 'Administrador')
        self.assertEqual(fisio.get_tipo_usuario_display(), 'Fisioterapeuta')


# ==============================================================================
# 2. AUTENTICACIÓN Y SEGURIDAD — PU-006 a PU-009
# ==============================================================================
class AutenticacionSeguridadTests(TestCase):
    """Pruebas unitarias para autenticación y mecanismos de seguridad"""

    def setUp(self):
        self.password_plano = 'ClaveSegura2026*'
        self.user = CustomUser.objects.create_user(
            username='seguridad_user',
            email='seguridad@kalesi.com',
            password=self.password_plano,
            tipo_usuario='ADMIN',
            document_number='SEC-001'
        )

    def test_password_hash(self):
        """PU-006: Verifica el almacenamiento seguro de contraseñas mediante hash."""
        self.assertNotEqual(self.user.password, self.password_plano)
        self.assertTrue(self.user.check_password(self.password_plano))
        self.assertTrue(self.user.has_usable_password())

    def test_credenciales_validas(self):
        """PU-007: Verifica la autenticación correcta con credenciales válidas."""
        authenticated_user = authenticate(
            username='seguridad_user',
            password=self.password_plano
        )
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user, self.user)

    def test_credenciales_invalidas(self):
        """PU-008: Verifica el rechazo de contraseñas incorrectas."""
        authenticated_user = authenticate(
            username='seguridad_user',
            password='PasswordErroneo999'
        )
        self.assertIsNone(authenticated_user)

    def test_usuario_inactivo(self):
        """PU-009: Verifica que un usuario desactivado no pueda autenticarse."""
        self.user.is_active = False
        self.user.save()

        authenticated_user = authenticate(
            username='seguridad_user',
            password=self.password_plano
        )
        self.assertIsNone(authenticated_user)


# ==============================================================================
# 3. MÓDULO DE PACIENTES — PU-010 a PU-015
# ==============================================================================
class ModuloPacientesTests(TestCase):
    """Pruebas unitarias para la ficha y gestión de pacientes"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.creador = CustomUser.objects.create_user(
            username='recep_pac',
            email='recep_pac@kalesi.com',
            password='pass',
            tipo_usuario='RECEP',
            document_number='CREA-001'
        )

    def test_crear_paciente(self):
        """PU-010: Verifica la creación de pacientes con datos válidos."""
        paciente = Patient.objects.create(
            nombres='Carlos',
            apellidos='Mendoza',
            tipo_documento=self.doc_type,
            documento_identidad='78945612',
            sexo='Masculino',
            fecha_nacimiento=date(1993, 6, 14),
            numero_telefono='77123456',
            direccion='Av. Heroínas 450',
            creado_por=self.creador
        )
        self.assertIsNotNone(paciente.pk)
        self.assertEqual(paciente.get_full_name(), 'Carlos Mendoza')
        self.assertTrue(paciente.estado)

    def test_documento_paciente_unico(self):
        """PU-011: Verifica la prevención de documentos duplicados en pacientes."""
        Patient.objects.create(
            nombres='Ana',
            apellidos='Roca',
            tipo_documento=self.doc_type,
            documento_identidad='DOC-DUP-01',
            sexo='Femenino',
            fecha_nacimiento=date(1990, 1, 1),
            numero_telefono='71111111',
            direccion='Calle 1'
        )
        with self.assertRaises(IntegrityError):
            Patient.objects.create(
                nombres='Beatriz',
                apellidos='Suarez',
                tipo_documento=self.doc_type,
                documento_identidad='DOC-DUP-01',
                sexo='Femenino',
                fecha_nacimiento=date(1992, 2, 2),
                numero_telefono='72222222',
                direccion='Calle 2'
            )

    def test_campos_obligatorios_paciente(self):
        """PU-012: Verifica los campos requeridos en el modelo de paciente."""
        paciente_invalido = Patient(
            nombres='',
            apellidos='',
            documento_identidad=''
        )
        with self.assertRaises(ValidationError):
            paciente_invalido.full_clean()

    def test_validar_fecha_nacimiento(self):
        """PU-013: Verifica las restricciones y cálculo de fecha de nacimiento y edad."""
        hoy = date.today()
        fecha_mayor = hoy.replace(year=hoy.year - 25)
        fecha_menor = hoy.replace(year=hoy.year - 10)

        paciente_adulto = Patient.objects.create(
            nombres='Adulto',
            apellidos='Mayor',
            tipo_documento=self.doc_type,
            documento_identidad='DOC-ADULTO',
            sexo='Masculino',
            fecha_nacimiento=fecha_mayor,
            numero_telefono='73333333',
            direccion='Calle 3'
        )
        paciente_joven = Patient.objects.create(
            nombres='Menor',
            apellidos='Edad',
            tipo_documento=self.doc_type,
            documento_identidad='DOC-MENOR',
            sexo='Femenino',
            fecha_nacimiento=fecha_menor,
            numero_telefono='74444444',
            direccion='Calle 4'
        )

        self.assertEqual(paciente_adulto.edad, 25)
        self.assertTrue(paciente_adulto.es_mayor)
        self.assertFalse(paciente_adulto.es_menor)

        self.assertEqual(paciente_joven.edad, 10)
        self.assertTrue(paciente_joven.es_menor)
        self.assertFalse(paciente_joven.es_mayor)

    def test_actualizar_paciente(self):
        """PU-014: Verifica la actualización de datos del paciente."""
        paciente = Patient.objects.create(
            nombres='Elena',
            apellidos='Torres',
            tipo_documento=self.doc_type,
            documento_identidad='ACT-001',
            sexo='Femenino',
            fecha_nacimiento=date(1988, 11, 20),
            numero_telefono='70000001',
            direccion='Dirección Antigua'
        )
        paciente.numero_telefono = '79999999'
        paciente.direccion = 'Dirección Actualizada 123'
        paciente.save()

        paciente_actualizado = Patient.objects.get(pk=paciente.pk)
        self.assertEqual(paciente_actualizado.numero_telefono, '79999999')
        self.assertEqual(paciente_actualizado.direccion, 'Dirección Actualizada 123')

    def test_desactivar_paciente(self):
        """PU-015: Verifica la desactivación lógica del paciente."""
        paciente = Patient.objects.create(
            nombres='Rodrigo',
            apellidos='Rios',
            tipo_documento=self.doc_type,
            documento_identidad='DESACT-01',
            sexo='Masculino',
            fecha_nacimiento=date(1995, 4, 15),
            numero_telefono='75555555',
            direccion='Calle 5'
        )
        self.assertTrue(paciente.estado)
        paciente.estado = False
        paciente.save()

        recuperado = Patient.objects.get(pk=paciente.pk)
        self.assertFalse(recuperado.estado)


# ==============================================================================
# 4. EXPEDIENTES CLÍNICOS — PU-016 a PU-020
# ==============================================================================
class ExpedientesClinicosTests(TestCase):
    """Pruebas unitarias para expedientes clínicos y su estructura"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.paciente = Patient.objects.create(
            nombres='Gabriela',
            apellidos='Fernandez',
            tipo_documento=self.doc_type,
            documento_identidad='EXP-PAC-01',
            sexo='Femenino',
            fecha_nacimiento=date(1996, 8, 12),
            numero_telefono='76666666',
            direccion='Av. América 800'
        )
        self.profesional = CustomUser.objects.create_user(
            username='fisio_exp',
            email='fisio_exp@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-EXP-01'
        )

    def test_crear_expediente(self):
        """PU-016: Verifica la creación automática/manual del expediente clínico."""
        expediente = getattr(self.paciente, 'expediente', None)
        if not expediente:
            expediente = Expediente.objects.create(paciente=self.paciente)
        self.assertIsNotNone(expediente.pk)
        self.assertTrue(expediente.numero_expediente.startswith('EXP-FIS-'))
        self.assertEqual(expediente.estado, 'ACTIVO')

    def test_asociar_expediente_paciente(self):
        """PU-017: Verifica la asociación correcta y bidireccional con el paciente."""
        expediente = self.paciente.expediente
        self.assertEqual(expediente.paciente, self.paciente)
        self.assertEqual(self.paciente.expediente, expediente)

    def test_validar_datos_clinicos(self):
        """PU-018: Verifica los campos clínicos obligatorios en la primera consulta."""
        consulta_invalida = PrimeraConsulta(
            expediente=self.paciente.expediente,
            profesional=self.profesional,
            motivo_consulta=''
        )
        with self.assertRaises(ValidationError):
            consulta_invalida.full_clean()

    def test_registrar_antecedentes(self):
        """PU-019: Verifica el almacenamiento de antecedentes clínicos."""
        primera = PrimeraConsulta.objects.create(
            expediente=self.paciente.expediente,
            profesional=self.profesional,
            motivo_consulta='Cervicalgia crónica',
            nivel_dolor_inicial=7,
            diabetes='Sin antecedentes familiares ni personales',
            alergias='Alergia leve a la penicilina',
            hipertension='Normotensa',
            cirugias_previas='Apendicectomía año 2015'
        )
        self.assertEqual(primera.diabetes, 'Sin antecedentes familiares ni personales')
        self.assertEqual(primera.alergias, 'Alergia leve a la penicilina')
        self.assertEqual(primera.cirugias_previas, 'Apendicectomía año 2015')

    def test_recuperar_expediente(self):
        """PU-020: Verifica la recuperación íntegra de los datos del expediente."""
        num = self.paciente.expediente.numero_expediente
        recuperado = Expediente.objects.get(numero_expediente=num)
        self.assertEqual(recuperado.paciente.get_full_name(), 'Gabriela Fernandez')
        self.assertEqual(recuperado.paciente.documento_identidad, 'EXP-PAC-01')


# ==============================================================================
# 5. GESTIÓN DE CITAS — PU-021 a PU-026
# ==============================================================================
class GestionCitasTests(TestCase):
    """Pruebas unitarias para programación y estados de citas médicas"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.paciente = Patient.objects.create(
            nombres='Mateo',
            apellidos='Silva',
            tipo_documento=self.doc_type,
            documento_identidad='CITA-PAC-01',
            sexo='Masculino',
            fecha_nacimiento=date(1991, 2, 28),
            numero_telefono='77778888',
            direccion='Calle Los Álamos 12'
        )
        self.profesional = CustomUser.objects.create_user(
            username='fisio_cita',
            email='fisio_cita@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-CITA-01'
        )
        self.profesional_2 = CustomUser.objects.create_user(
            username='fisio_cita_2',
            email='fisio_cita2@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-CITA-02'
        )
        self.fecha_cita = timezone.now() + timedelta(days=2)

    def test_crear_cita(self):
        """PU-021: Verifica el registro de citas válidas."""
        cita = Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=45,
            motivo='Evaluación inicial de hombro',
            tipo_cita='PRIMERA_CONSULTA',
            estado='PENDIENTE'
        )
        self.assertIsNotNone(cita.pk)
        self.assertEqual(cita.estado, 'PENDIENTE')
        self.assertEqual(cita.numero_sesion, 1)

    def test_fecha_cita_valida(self):
        """PU-022: Verifica las restricciones de fecha y tipo de cita."""
        cita = Cita(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Consulta regular',
            tipo_cita='TIPO_INEXISTENTE'
        )
        with self.assertRaises(ValidationError):
            cita.clean()

    def test_conflicto_horario(self):
        """PU-023: Verifica la prevención de horarios ocupados para el mismo profesional."""
        Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Cita inicial',
            tipo_cita='PRIMERA_CONSULTA',
            estado='PENDIENTE'
        )
        # La restricción de base de datos unique_profesional_fecha previene duplicado exacto
        with self.assertRaises(IntegrityError):
            Cita.objects.create(
                paciente=self.paciente,
                profesional=self.profesional,
                fecha=self.fecha_cita,
                duracion=30,
                motivo='Cita en conflicto',
                tipo_cita='SEGUIMIENTO',
                estado='PENDIENTE'
            )

    def test_disponibilidad_profesional(self):
        """PU-024: Verifica la disponibilidad del profesional de forma independiente."""
        Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Cita primer terapeuta',
            tipo_cita='PRIMERA_CONSULTA'
        )
        # Otro profesional puede atender a la misma hora sin conflicto
        cita_otro = Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional_2,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Cita segundo terapeuta',
            tipo_cita='PRIMERA_CONSULTA'
        )
        self.assertIsNotNone(cita_otro.pk)

    def test_reprogramar_cita(self):
        """PU-025: Verifica la actualización de fecha, hora y estado al reprogramar."""
        cita = Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Cita a reprogramar',
            tipo_cita='PRIMERA_CONSULTA'
        )
        nueva_fecha = self.fecha_cita + timedelta(days=1, hours=2)
        cita.fecha = nueva_fecha
        cita.estado = 'REPROGRAMADA'
        cita.save()

        recuperada = Cita.objects.get(pk=cita.pk)
        self.assertEqual(recuperada.fecha, nueva_fecha)
        self.assertEqual(recuperada.estado, 'REPROGRAMADA')

    def test_cancelar_cita(self):
        """PU-026: Verifica la actualización del estado de la cita al cancelar."""
        cita = Cita.objects.create(
            paciente=self.paciente,
            profesional=self.profesional,
            fecha=self.fecha_cita,
            duracion=30,
            motivo='Cita a cancelar',
            tipo_cita='PRIMERA_CONSULTA'
        )
        cita.estado = 'CANCELADA'
        cita.save()

        recuperada = Cita.objects.get(pk=cita.pk)
        self.assertEqual(recuperada.estado, 'CANCELADA')


# ==============================================================================
# 6. SEGUIMIENTO FISIOTERAPÉUTICO — PU-027 a PU-031
# ==============================================================================
class SeguimientoFisioterapeuticoTests(TestCase):
    """Pruebas unitarias para consultas iniciales y sesiones de evolución"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.paciente = Patient.objects.create(
            nombres='Lorena',
            apellidos='Castro',
            tipo_documento=self.doc_type,
            documento_identidad='SEG-PAC-01',
            sexo='Femenino',
            fecha_nacimiento=date(1994, 10, 5),
            numero_telefono='78881122',
            direccion='Calle Ballivián 200'
        )
        self.expediente = self.paciente.expediente
        self.profesional = CustomUser.objects.create_user(
            username='fisio_lorena',
            email='lorena_f@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-SEG-01'
        )

    def test_registrar_evaluacion_inicial(self):
        """PU-027: Verifica la creación de una evaluación inicial (Primera Consulta)."""
        primera = PrimeraConsulta.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            motivo_consulta='Dolor en hombro derecho post-traumático',
            nivel_dolor_inicial=8,
            localizacion_dolor='Manguito rotador derecho'
        )
        self.assertIsNotNone(primera.pk)
        self.assertTrue(self.expediente.tiene_primera_consulta)
        self.assertEqual(self.expediente.primera_consulta.nivel_dolor_inicial, 8)

    def test_registrar_seguimiento(self):
        """PU-028: Verifica el registro de sesiones de seguimiento."""
        seguimiento = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=6,
            evolucion_paciente='Disminución del dolor tras terapia manual',
            localizacion_dolor='Hombro derecho'
        )
        self.assertIsNotNone(seguimiento.pk)
        self.assertEqual(seguimiento.numero_sesion, 1)
        self.assertEqual(seguimiento.nivel_dolor_actual, 6)

    def test_asociar_sesion_paciente(self):
        """PU-029: Verifica la vinculación directa del seguimiento al paciente."""
        seguimiento = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=5,
            evolucion_paciente='Sesión de ultrasonido y ejercicios'
        )
        self.assertEqual(seguimiento.expediente.paciente, self.paciente)

    def test_validar_nivel_dolor(self):
        """PU-030: Verifica los valores permitidos para el nivel de dolor (0 a 10)."""
        valores_validos = [n[0] for n in BaseEvaluacionDolor.NIVEL_DOLOR]
        self.assertIn(0, valores_validos)
        self.assertIn(5, valores_validos)
        self.assertIn(10, valores_validos)
        self.assertNotIn(11, valores_validos)
        self.assertNotIn(-1, valores_validos)

    def test_consultar_evolucion(self):
        """PU-031: Verifica la recuperación de indicadores clínicos registrados."""
        ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=8,
            evolucion_paciente='Inicio de tratamiento'
        )
        ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=2,
            nivel_dolor_actual=5,
            evolucion_paciente='Evolución favorable'
        )

        self.assertEqual(self.expediente.total_sesiones, 2)
        sesiones = list(self.expediente.sesiones_seguimiento)
        self.assertEqual(sesiones[0].nivel_dolor_actual, 8)
        self.assertEqual(sesiones[1].nivel_dolor_actual, 5)


# ==============================================================================
# 7. CUESTIONARIOS FISIOTERAPÉUTICOS — PU-032 a PU-036
# ==============================================================================
class CuestionariosFisioterapeuticosTests(TestCase):
    """Pruebas unitarias para cuestionarios, preguntas y respuestas clínicas"""

    def setUp(self):
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.paciente = Patient.objects.create(
            nombres='Andres',
            apellidos='Guzman',
            tipo_documento=self.doc_type,
            documento_identidad='CUEST-PAC-01',
            sexo='Masculino',
            fecha_nacimiento=date(1989, 3, 17),
            numero_telefono='71239874',
            direccion='Calle Sucre 10'
        )
        self.expediente = self.paciente.expediente
        self.profesional = CustomUser.objects.create_user(
            username='fisio_cuest',
            email='cuest@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-CUEST-01'
        )
        self.seguimiento = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=7,
            evolucion_paciente='Sesión de evaluación'
        )

    def test_crear_cuestionario(self):
        """PU-032: Verifica la creación de un cuestionario válido."""
        cuestionario = Cuestionario.objects.create(
            nombre='Evaluación Lumbar',
            descripcion='Cuestionario funcional de columna lumbar',
            tipo_cuestionario='ESPALDA',
            activo=True,
            created_by=self.profesional
        )
        self.assertIsNotNone(cuestionario.pk)
        self.assertEqual(cuestionario.nombre, 'Evaluación Lumbar')
        self.assertTrue(cuestionario.activo)

    def test_asociar_region_anatomica(self):
        """PU-033: Verifica la asociación correcta con una región anatómica."""
        cuestionario = Cuestionario.objects.create(
            nombre='Evaluación de Hombro',
            descripcion='Dolor y movilidad de hombro',
            tipo_cuestionario='HOMBRO_PECTORAL'
        )
        self.assertEqual(cuestionario.tipo_cuestionario, 'HOMBRO_PECTORAL')
        self.assertEqual(cuestionario.get_tipo_cuestionario_display(), 'Hombro y Pectoral')

    def test_validar_preguntas(self):
        """PU-034: Verifica las condiciones de configuración y validación de preguntas."""
        cuestionario = Cuestionario.objects.create(
            nombre='Cuestionario Rodilla',
            descripcion='Evaluación rodilla',
            tipo_cuestionario='RODILLA'
        )
        pregunta = PreguntaCuestionario.objects.create(
            cuestionario=cuestionario,
            texto_pregunta='¿Nivel de dolor al flexionar la rodilla?',
            tipo_pregunta='ESCALA_NUMERICA',
            orden=1,
            obligatorio=True,
            escala_min=0,
            escala_max=10,
            etiqueta_min='Sin dolor',
            etiqueta_max='Incapacitante',
            es_indicador_clave=True,
            umbral_alarma=6
        )
        self.assertEqual(pregunta.escala_min, 0)
        self.assertEqual(pregunta.escala_max, 10)
        self.assertTrue(pregunta.es_indicador_clave)
        self.assertEqual(cuestionario.preguntas.count(), 1)

    def test_registrar_respuestas(self):
        """PU-035: Verifica el almacenamiento de respuestas del paciente."""
        cuestionario = Cuestionario.objects.create(
            nombre='Test Cuestionario',
            descripcion='Test',
            tipo_cuestionario='GENERAL'
        )
        pregunta = PreguntaCuestionario.objects.create(
            cuestionario=cuestionario,
            texto_pregunta='¿Dolor matutino?',
            tipo_pregunta='ESCALA',
            orden=1
        )
        respuesta = RespuestaCuestionario.objects.create(
            consulta_seguimiento=self.seguimiento,
            pregunta=pregunta,
            respuesta_escala=6
        )
        self.assertEqual(respuesta.valor_respuesta, 6)
        self.assertEqual(respuesta.respuesta_escala, 6)

    def test_asociar_respuestas_paciente(self):
        """PU-036: Verifica la asociación de las respuestas con el paciente."""
        cuestionario = Cuestionario.objects.create(
            nombre='Test',
            descripcion='Test',
            tipo_cuestionario='GENERAL'
        )
        pregunta = PreguntaCuestionario.objects.create(
            cuestionario=cuestionario,
            texto_pregunta='Pregunta 1',
            tipo_pregunta='TEXTO'
        )
        respuesta = RespuestaCuestionario.objects.create(
            consulta_seguimiento=self.seguimiento,
            pregunta=pregunta,
            respuesta_texto='El dolor disminuye en reposo'
        )
        paciente_asociado = respuesta.consulta_seguimiento.expediente.paciente
        self.assertEqual(paciente_asociado, self.paciente)


# ==============================================================================
# 8. ANÁLISIS PREDICTIVO — PU-037 a PU-040
# ==============================================================================
class AnalisisPredictivoTests(TestCase):
    """Pruebas unitarias para el motor predictivo y cálculos evolutivos"""

    def setUp(self):
        self.service = AnalisisPredictivoService()
        self.doc_type = DocumentType.objects.create(
            document_type="CI",
            document_description="Cédula de Identidad"
        )
        self.paciente = Patient.objects.create(
            nombres='Samuel',
            apellidos='Flores',
            tipo_documento=self.doc_type,
            documento_identidad='PRED-PAC-01',
            sexo='Masculino',
            fecha_nacimiento=date(1987, 5, 23),
            numero_telefono='73334455',
            direccion='Calle España 15'
        )
        self.expediente = self.paciente.expediente
        self.profesional = CustomUser.objects.create_user(
            username='fisio_pred',
            email='pred@kalesi.com',
            password='pass',
            tipo_usuario='FISIO',
            document_number='F-PRED-01'
        )
        self.cuestionario = Cuestionario.objects.create(
            nombre='Evaluación Hombro Predictivo',
            descripcion='Test predictivo',
            tipo_cuestionario='HOMBRO_PECTORAL'
        )
        self.pregunta_escala = PreguntaCuestionario.objects.create(
            cuestionario=self.cuestionario,
            texto_pregunta='Dolor de hombro al elevar el brazo',
            tipo_pregunta='ESCALA_NUMERICA',
            orden=1,
            escala_min=0,
            escala_max=10
        )
        self.pregunta_texto = PreguntaCuestionario.objects.create(
            cuestionario=self.cuestionario,
            texto_pregunta='Observaciones del paciente',
            tipo_pregunta='TEXTO',
            orden=2
        )

    def test_validar_datos_entrada(self):
        """PU-037: Verifica la validación de los datos utilizados por el análisis."""
        sesion = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=8,
            evolucion_paciente='Sesión 1'
        )
        # Las preguntas de texto NO deben alimentar el análisis predictivo de escalas
        resp_texto = RespuestaCuestionario.objects.create(
            consulta_seguimiento=sesion,
            pregunta=self.pregunta_texto,
            respuesta_texto='Molestia continua'
        )
        resultado_texto = self.service.sincronizar_respuesta_escala(resp_texto)
        self.assertIsNone(resultado_texto)

        # Las preguntas de escala SÍ deben procesarse y normalizarse
        resp_escala = RespuestaCuestionario.objects.create(
            consulta_seguimiento=sesion,
            pregunta=self.pregunta_escala,
            respuesta_escala=8
        )
        resultado_escala = self.service.sincronizar_respuesta_escala(resp_escala)
        self.assertIsNotNone(resultado_escala)
        self.assertEqual(resultado_escala.valor_escala, 8)
        self.assertEqual(resultado_escala.valor_normalizado, 0.8)

    def test_procesar_indicadores(self):
        """PU-038: Verifica el procesamiento de indicadores clínicos (tendencia y variación)."""
        # Sesión 1: dolor 8
        s1 = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=1,
            nivel_dolor_actual=8,
            evolucion_paciente='Sesión 1'
        )
        r1 = RespuestaCuestionario.objects.create(
            consulta_seguimiento=s1,
            pregunta=self.pregunta_escala,
            respuesta_escala=8
        )
        self.service.sincronizar_respuesta_escala(r1)

        # Sesión 2: dolor 5 (mejoría)
        s2 = ConsultaSegumiento.objects.create(
            expediente=self.expediente,
            profesional=self.profesional,
            numero_sesion=2,
            nivel_dolor_actual=5,
            evolucion_paciente='Sesión 2'
        )
        r2 = RespuestaCuestionario.objects.create(
            consulta_seguimiento=s2,
            pregunta=self.pregunta_escala,
            respuesta_escala=5
        )
        analisis_s2 = self.service.sincronizar_respuesta_escala(r2)

        self.assertIsNotNone(analisis_s2)
        self.assertEqual(analisis_s2.tendencia, 'MEJORANDO')
        self.assertIsNotNone(analisis_s2.variacion_porcentual)
        self.assertLess(analisis_s2.variacion_porcentual, 0)  # Variación negativa = reducción del dolor

    def test_generar_prediccion(self):
        """PU-039: Verifica la generación de un resultado predictivo válido (regresión con 3 mediciones)."""
        valores_dolor = [9, 6, 3]  # Tendencia descendente lineal clara
        for i, val in enumerate(valores_dolor, start=1):
            s = ConsultaSegumiento.objects.create(
                expediente=self.expediente,
                profesional=self.profesional,
                numero_sesion=i,
                nivel_dolor_actual=val,
                evolucion_paciente=f'Sesión {i}'
            )
            r = RespuestaCuestionario.objects.create(
                consulta_seguimiento=s,
                pregunta=self.pregunta_escala,
                respuesta_escala=val
            )
            self.service.sincronizar_respuesta_escala(r)

        ultima_medicion = AnalisisPredictivoEscala.objects.filter(
            consulta_seguimiento__expediente=self.expediente,
            pregunta=self.pregunta_escala
        ).order_by('sesion_numero').last()

        self.assertIsNotNone(ultima_medicion.prediccion_siguiente)
        # 9 -> 6 -> 3 con pendiente -3 proyecta aproximadamente 0 para la sesión 4
        self.assertLessEqual(ultima_medicion.prediccion_siguiente, 3)

    def test_validar_resultado_prediccion(self):
        """PU-040: Verifica el formato y los valores de salida del análisis predictivo y resumen."""
        valores_dolor = [7, 6, 5]
        for i, val in enumerate(valores_dolor, start=1):
            s = ConsultaSegumiento.objects.create(
                expediente=self.expediente,
                profesional=self.profesional,
                numero_sesion=i,
                nivel_dolor_actual=val,
                evolucion_paciente=f'Sesión {i}'
            )
            r = RespuestaCuestionario.objects.create(
                consulta_seguimiento=s,
                pregunta=self.pregunta_escala,
                respuesta_escala=val
            )
            self.service.sincronizar_respuesta_escala(r)

        ultima_medicion = AnalisisPredictivoEscala.objects.filter(
            consulta_seguimiento__expediente=self.expediente,
            pregunta=self.pregunta_escala
        ).order_by('sesion_numero').last()

        # Validación de rangos en escala de 0 a 10
        self.assertGreaterEqual(ultima_medicion.prediccion_siguiente, 0)
        self.assertLessEqual(ultima_medicion.prediccion_siguiente, 10)
        self.assertGreaterEqual(ultima_medicion.intervalo_confianza_min, 0)
        self.assertLessEqual(ultima_medicion.intervalo_confianza_max, 10)
        self.assertLessEqual(
            ultima_medicion.intervalo_confianza_min,
            ultima_medicion.intervalo_confianza_max
        )

        # Validación del registro de EvoluciónPaciente
        evolucion = EvolucionPaciente.objects.get(
            expediente=self.expediente,
            pregunta_relacionada=self.pregunta_escala
        )
        self.assertEqual(evolucion.numero_sesiones, 3)
        self.assertEqual(evolucion.primera_medicion, 7.0)
        self.assertEqual(evolucion.ultima_medicion, 5.0)
        self.assertEqual(evolucion.tendencia_general, 'MEJORANDO')
